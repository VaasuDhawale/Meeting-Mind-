"""
Meeting Intelligence API Endpoints.
Handles media upload, multimodal AI processing, persistence, dynamic report generation, and multi-format exports.
"""

import os
import shutil
import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import MeetingSession
from app.db.session import get_db
from app.services.demo_generator import ensure_demo_media
from app.services.media_service import (
    analyze_video_opencv,
    extract_audio_from_video,
    extract_document_structure,
    extract_document_text,
    save_upload_file,
    validate_document_file,
    validate_media_file,
)
from app.services.nlp_ai_service import analyze_meeting_intelligence
from app.services.pdf_service import generate_meeting_pdf_report
from app.services.docx_service import generate_meeting_docx_report
from app.services.report_engine import generate_json_export, generate_markdown_report
from app.services.transcription_service import transcribe_audio

logger = structlog.get_logger()
router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post(
    "/analyze",
    summary="Analyze Video/Audio Meeting Session",
    description="Upload a video or audio meeting session with optional document to execute the full multimodal AI pipeline.",
)
async def analyze_session(
    title: str = Form("Meeting Intelligence Session"),
    file: UploadFile = Form(...),
    document: UploadFile | None = Form(None),
    api_key: str | None = Form(None),
    provider: str | None = Form("auto"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Execute complete multimodal AI pipeline for an uploaded meeting."""
    # 1. Validation
    file_type, clean_media_name = validate_media_file(file)
    session_id = str(uuid.uuid4())

    # Create session directory
    session_upload_dir = os.path.join(settings.upload_dir, session_id)
    os.makedirs(session_upload_dir, exist_ok=True)

    media_ext = os.path.splitext(clean_media_name)[1]
    saved_media_path = os.path.join(session_upload_dir, f"source{media_ext}")
    await save_upload_file(file, saved_media_path, settings.max_video_size_mb)

    # Document handling if uploaded
    document_name = None
    saved_doc_path = None
    doc_text = ""
    doc_structure = None
    if document and document.filename:
        clean_doc_name = validate_document_file(document)
        document_name = clean_doc_name
        doc_ext = os.path.splitext(clean_doc_name)[1]
        saved_doc_path = os.path.join(session_upload_dir, f"document{doc_ext}")
        await save_upload_file(document, saved_doc_path, settings.max_document_size_mb)
        doc_structure = extract_document_structure(saved_doc_path)
        doc_text = doc_structure.get("full_text", "")

    # 2. Multimodal Video & Audio Processing
    audio_path = os.path.join(session_upload_dir, "extracted_audio.wav")
    video_meta: dict[str, Any] = {}

    if file_type == "video":
        logger.info("Extracting video keyframes and visual intelligence with OpenCV")
        video_meta = analyze_video_opencv(saved_media_path, session_id)
        has_audio = extract_audio_from_video(saved_media_path, audio_path)
    else:
        # File is audio
        audio_path = saved_media_path
        has_audio = True
        video_meta = {
            "duration_seconds": 60.0,
            "keyframes": [],
            "scene_changes": 0,
            "visual_activity": 0.0,
        }

    # 3. Speech-to-Text Transcription
    transcript_text = ""
    transcript_segments = []
    trans_res: dict[str, Any] = {}
    if has_audio and os.path.exists(audio_path):
        logger.info("Transcribing audio stream")
        trans_res = await transcribe_audio(audio_path, custom_api_key=api_key, preferred_provider=provider)
        transcript_text = trans_res.get("text", "")
        transcript_segments = trans_res.get("segments", [])

    if not transcript_text and doc_text:
        transcript_text = f"[Synthesized from Agenda & Notes]:\n{doc_text[:3000]}"

    # Derive clean title from filename or speech if title is generic
    from app.services.nlp_ai_service import clean_title_from_context
    derived_title = clean_title_from_context(title, clean_media_name, transcript_segments)

    # 4. AI / ML Intelligence Synthesis
    duration = video_meta.get("duration_seconds", 0.0)
    ai_results = await analyze_meeting_intelligence(
        transcript_text=transcript_text,
        document_text=doc_text,
        video_metadata=video_meta,
        document_structure=doc_structure,
        custom_api_key=api_key,
        preferred_provider=provider,
        transcript_segments=transcript_segments,
        session_title=derived_title,
    )

    # Augment keyframes with quotes & evidence timestamps
    augmented_kf = ai_results.get("augmented_keyframes")
    if augmented_kf:
        video_meta["keyframes"] = augmented_kf
    video_meta["transcript_segments"] = transcript_segments
    video_meta["transcript_lines"] = ai_results.get("transcript_lines", [])
    video_meta["meeting_overview"] = ai_results.get("meeting_overview")
    video_meta["key_discussion_points"] = ai_results.get("key_discussion_points", [])
    video_meta["open_questions"] = ai_results.get("open_questions", [])
    video_meta["risks_blockers"] = ai_results.get("risks_blockers", [])
    video_meta["important_moments"] = ai_results.get("important_moments", [])
    video_meta["topics_mind_map"] = ai_results.get("topics_mind_map", [])

    # 5. Database Record Creation
    session = MeetingSession(
        id=session_id,
        title=derived_title,
        status="completed",
        source_filename=clean_media_name,
        source_file_type=file_type,
        file_path=saved_media_path,
        duration_seconds=duration,
        document_filename=document_name,
        document_path=saved_doc_path,
        ai_provider=ai_results.get("ai_provider", trans_res.get("provider", "Local ML Engine")),
        transcript=transcript_text or "(No distinct vocal stream detected)",
        summary=ai_results.get("summary", ""),
        action_items=ai_results.get("action_items", []),
        decisions=ai_results.get("decisions", []),
        topics=ai_results.get("topics", []),
        sentiment=ai_results.get("sentiment", {}),
        video_analysis=video_meta,
        speakers=ai_results.get("speakers", []),
        questions_answers=ai_results.get("questions_answers", []),
        timeline=ai_results.get("timeline", []),
        document_analysis=ai_results.get("document_analysis", {}),
        evidence=ai_results.get("evidence", []),
    )

    # 6. Generate Reports (PDF and Word DOCX)
    session_dict = session.to_dict()
    session_dict["meeting_overview"] = ai_results.get("meeting_overview")
    session_dict["key_discussion_points"] = ai_results.get("key_discussion_points")
    session_dict["open_questions"] = ai_results.get("open_questions")
    session_dict["risks_blockers"] = ai_results.get("risks_blockers")
    session_dict["important_moments"] = ai_results.get("important_moments")
    session_dict["topics_mind_map"] = ai_results.get("topics_mind_map")
    session_dict["augmented_keyframes"] = ai_results.get("augmented_keyframes")
    session_dict["transcript_lines"] = ai_results.get("transcript_lines")
    session_dict["transcript_segments"] = transcript_segments

    pdf_file_path = generate_meeting_pdf_report(session_dict, session_id)
    session.pdf_path = pdf_file_path

    try:
        docx_file_path = generate_meeting_docx_report(session_dict, session_id)
        session.docx_path = docx_file_path
    except Exception as exc:
        logger.error("Failed to generate Word report on analyze", error=str(exc))

    db.add(session)
    await db.commit()
    await db.refresh(session)

    logger.info("Meeting session analysis successfully completed", session_id=session_id)
    return session.to_dict()


@router.post(
    "/demo",
    summary="Run Faculty Demo Analysis",
    description="Runs the real end-to-end multimodal pipeline using realistic pre-packaged sample meeting data.",
)
async def run_faculty_demo(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Execute complete analysis on real faculty demo dataset."""
    video_path, agenda_path = ensure_demo_media()
    session_id = str(uuid.uuid4())
    session_upload_dir = os.path.join(settings.upload_dir, session_id)
    os.makedirs(session_upload_dir, exist_ok=True)

    # Copy demo media into session dir
    dest_video = os.path.join(session_upload_dir, "faculty_demo_meeting.mp4")
    shutil.copyfile(video_path, dest_video)

    doc_structure = extract_document_structure(agenda_path)
    doc_text = doc_structure.get("full_text", "")

    # OpenCV Analysis
    video_meta = analyze_video_opencv(dest_video, session_id)

    # Extract audio
    audio_path = os.path.join(session_upload_dir, "extracted_audio.wav")
    has_audio = extract_audio_from_video(dest_video, audio_path)

    # Transcribe
    trans_text = ""
    trans_segments = []
    trans_res: dict[str, Any] = {}
    if has_audio and os.path.exists(audio_path):
        trans_res = await transcribe_audio(audio_path)
        trans_text = trans_res.get("text", "")
        trans_segments = trans_res.get("segments", [])

    # Multi-modal fusion with agenda text
    full_transcript = (
        f"{doc_text}\n\n[Live Audio Track Speech-to-Text]: {trans_text}"
        if trans_text
        else doc_text
    )

    # AI / ML Synthesis
    ai_results = await analyze_meeting_intelligence(
        transcript_text=full_transcript,
        document_text=doc_text,
        video_metadata=video_meta,
        document_structure=doc_structure,
        transcript_segments=trans_segments,
        session_title="Faculty Demo: Multimodal Meeting Intelligence Review",
    )

    # Augment keyframes with quotes & evidence timestamps
    augmented_kf = ai_results.get("augmented_keyframes")
    if augmented_kf:
        video_meta["keyframes"] = augmented_kf
    video_meta["transcript_segments"] = trans_segments
    video_meta["transcript_lines"] = ai_results.get("transcript_lines", [])
    video_meta["meeting_overview"] = ai_results.get("meeting_overview")
    video_meta["key_discussion_points"] = ai_results.get("key_discussion_points", [])
    video_meta["open_questions"] = ai_results.get("open_questions", [])
    video_meta["risks_blockers"] = ai_results.get("risks_blockers", [])
    video_meta["important_moments"] = ai_results.get("important_moments", [])
    video_meta["topics_mind_map"] = ai_results.get("topics_mind_map", [])

    session = MeetingSession(
        id=session_id,
        title="Faculty Demo: Multimodal Meeting Intelligence Review",
        status="completed",
        source_filename="faculty_demo_meeting.mp4",
        source_file_type="video",
        file_path=dest_video,
        duration_seconds=video_meta.get("duration_seconds", 8.0),
        document_filename="faculty_demo_agenda.txt",
        document_path=agenda_path,
        ai_provider=ai_results.get("ai_provider", "Local ML Engine"),
        transcript=full_transcript,
        summary=ai_results.get("summary", ""),
        action_items=ai_results.get("action_items", []),
        decisions=ai_results.get("decisions", []),
        topics=ai_results.get("topics", []),
        sentiment=ai_results.get("sentiment", {}),
        video_analysis=video_meta,
        speakers=ai_results.get("speakers", []),
        questions_answers=ai_results.get("questions_answers", []),
        timeline=ai_results.get("timeline", []),
        document_analysis=ai_results.get("document_analysis", {}),
        evidence=ai_results.get("evidence", []),
    )

    session_dict = session.to_dict()
    session_dict["meeting_overview"] = ai_results.get("meeting_overview")
    session_dict["key_discussion_points"] = ai_results.get("key_discussion_points")
    session_dict["open_questions"] = ai_results.get("open_questions")
    session_dict["risks_blockers"] = ai_results.get("risks_blockers")
    session_dict["important_moments"] = ai_results.get("important_moments")
    session_dict["topics_mind_map"] = ai_results.get("topics_mind_map")
    session_dict["augmented_keyframes"] = ai_results.get("augmented_keyframes")
    session_dict["transcript_lines"] = ai_results.get("transcript_lines")
    session_dict["transcript_segments"] = trans_segments

    pdf_path = generate_meeting_pdf_report(session_dict, session_id)
    session.pdf_path = pdf_path

    try:
        docx_path = generate_meeting_docx_report(session_dict, session_id)
        session.docx_path = docx_path
    except Exception as exc:
        logger.error("Failed to generate Word report on demo", error=str(exc))

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session.to_dict()


@router.get(
    "",
    summary="List All Meeting Sessions",
    description="Retrieve all saved meeting intelligence sessions.",
)
async def list_sessions(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    """Return all historical sessions."""
    result = await db.execute(select(MeetingSession).order_by(desc(MeetingSession.created_at)))
    sessions = result.scalars().all()
    return [s.to_dict() for s in sessions]


@router.get(
    "/{session_id}",
    summary="Get Meeting Session Details",
)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Return single session details."""
    result = await db.execute(select(MeetingSession).where(MeetingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meeting session not found")
    return session.to_dict()


@router.get(
    "/{session_id}/json",
    summary="Export Structured Intelligence Data as JSON",
    description="Returns the standardized dynamic report JSON export.",
)
async def export_session_json(session_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Export session data in structured JSON format."""
    result = await db.execute(select(MeetingSession).where(MeetingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meeting session not found")
    return generate_json_export(session.to_dict())


@router.get(
    "/{session_id}/markdown",
    summary="Download Dynamic Report as Markdown",
    description="Download a structured, evidence-backed GitHub Flavored Markdown report.",
)
async def download_markdown_report(session_id: str, db: AsyncSession = Depends(get_db)) -> FileResponse:
    """Download Markdown dynamic report."""
    result = await db.execute(select(MeetingSession).where(MeetingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meeting session not found")

    md_content = generate_markdown_report(session.to_dict())
    md_path = os.path.join(settings.reports_dir, f"report_{session_id}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return FileResponse(
        path=md_path,
        filename=f"Meeting_Report_{session_id[:8]}.md",
        media_type="text/markdown",
        content_disposition_type="attachment",
    )


@router.get(
    "/{session_id}/txt",
    summary="Download Dynamic Report as Plain Text",
    description="Download a clean text version of the dynamic intelligence report.",
)
async def download_text_report(session_id: str, db: AsyncSession = Depends(get_db)) -> FileResponse:
    """Download plain text dynamic report."""
    result = await db.execute(select(MeetingSession).where(MeetingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meeting session not found")

    txt_content = generate_markdown_report(session.to_dict())
    txt_path = os.path.join(settings.reports_dir, f"report_{session_id}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)

    return FileResponse(
        path=txt_path,
        filename=f"Meeting_Report_{session_id[:8]}.txt",
        media_type="text/plain",
        content_disposition_type="attachment",
    )


@router.get(
    "/{session_id}/pdf",
    summary="Download or View Generated PDF Report",
)
async def download_pdf_report(
    session_id: str,
    inline: bool = False,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download or view the official ReportLab generated dynamic PDF report."""
    result = await db.execute(select(MeetingSession).where(MeetingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meeting session not found")

    pdf_path = session.pdf_path
    if not pdf_path or not os.path.exists(pdf_path):
        # Regenerate on the fly if needed
        pdf_path = generate_meeting_pdf_report(session.to_dict(), session_id)
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Could not generate PDF report")
        session.pdf_path = pdf_path
        await db.commit()

    filename = f"MeetingMind_Executive_Report_{session_id}.pdf"
    headers = {
        "Content-Disposition": f'{"inline" if inline else "attachment"}; filename="{filename}"',
    }
    return FileResponse(
        path=pdf_path,
        filename=filename,
        media_type="application/pdf",
        content_disposition_type="inline" if inline else "attachment",
        headers=headers,
    )


@router.get(
    "/{session_id}/docx",
    summary="Download Generated Microsoft Word Report (.docx)",
    description="Download a structured, professional, editable Microsoft Word intelligence document.",
)
async def download_docx_report(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download official Microsoft Word (.docx) intelligence report."""
    result = await db.execute(select(MeetingSession).where(MeetingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meeting session not found")

    docx_path = session.docx_path
    if not docx_path or not os.path.exists(docx_path):
        # Query previous session for progress comparison if available
        prev_result = await db.execute(
            select(MeetingSession)
            .where(MeetingSession.id != session_id)
            .order_by(desc(MeetingSession.created_at))
            .limit(1)
        )
        prev_session = prev_result.scalar_one_or_none()
        prev_data = prev_session.to_dict() if prev_session else None

        docx_path = generate_meeting_docx_report(session.to_dict(), session_id, prev_data)
        if not docx_path or not os.path.exists(docx_path):
            raise HTTPException(status_code=500, detail="Could not generate Word report")
        session.docx_path = docx_path
        await db.commit()

    filename = f"Meeting_Intelligence_{session_id[:8]}.docx"
    return FileResponse(
        path=docx_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        content_disposition_type="attachment",
    )


@router.get(
    "/{session_id}/transcript-pdf",
    summary="Download or View Full Verbatim Transcription as PDF",
)
async def download_transcript_pdf(
    session_id: str,
    inline: bool = False,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download or view a dedicated PDF containing the full verbatim transcription and dialogue."""
    from app.services.pdf_service import generate_transcript_pdf

    result = await db.execute(select(MeetingSession).where(MeetingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meeting session not found")

    transcript_pdf_path = generate_transcript_pdf(session.to_dict(), session_id)
    if not transcript_pdf_path or not os.path.exists(transcript_pdf_path):
        raise HTTPException(status_code=500, detail="Could not generate transcript PDF")

    filename = f"MeetingMind_Transcript_{session_id}.pdf"
    headers = {
        "Content-Disposition": f'{"inline" if inline else "attachment"}; filename="{filename}"',
    }
    return FileResponse(
        path=transcript_pdf_path,
        filename=filename,
        media_type="application/pdf",
        content_disposition_type="inline" if inline else "attachment",
        headers=headers,
    )


@router.get(
    "/{session_id}/transcript-txt",
    summary="Download Raw Transcript as Text File",
)
async def download_transcript_txt(session_id: str, db: AsyncSession = Depends(get_db)) -> FileResponse:
    """Download raw transcript as .txt file."""
    result = await db.execute(select(MeetingSession).where(MeetingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meeting session not found")

    txt_filename = f"transcript_{session_id}.txt"
    txt_path = os.path.join(settings.reports_dir, txt_filename)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"MEETING TRANSCRIPTION: {session.title}\n")
        f.write(f"Date: {session.created_at}\n")
        f.write(f"AI Provider: {session.ai_provider}\n")
        f.write("=" * 60 + "\n\n")
        f.write(session.transcript or "No transcript recorded.")

    return FileResponse(
        path=txt_path,
        filename=f"Transcription_{session_id[:8]}.txt",
        media_type="text/plain",
    )


@router.delete(
    "/{session_id}",
    summary="Delete Meeting Session",
)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Delete a meeting session and purge files."""
    result = await db.execute(select(MeetingSession).where(MeetingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meeting session not found")

    # Clean up directories
    session_upload_dir = os.path.join(settings.upload_dir, session_id)
    session_keyframes_dir = os.path.join(settings.keyframes_dir, session_id)
    for d in [session_upload_dir, session_keyframes_dir]:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)

    if session.pdf_path and os.path.exists(session.pdf_path):
        try:
            os.remove(session.pdf_path)
        except OSError:
            pass

    if session.docx_path and os.path.exists(session.docx_path):
        try:
            os.remove(session.docx_path)
        except OSError:
            pass

    await db.delete(session)
    await db.commit()
    return {"message": "Session deleted successfully"}
