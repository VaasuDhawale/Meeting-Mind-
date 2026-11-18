"""
Media Processing Service: Video/Audio extraction, OpenCV scene analysis, Document parsing.
"""

import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any

import cv2
import structlog
from fastapi import HTTPException, UploadFile

from app.config import settings

logger = structlog.get_logger()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and special character issues."""
    name = Path(filename).name
    name = re.sub(r"[^\w\s\.-]", "", name)
    return name.strip() or "media_upload"


def validate_media_file(file: UploadFile) -> tuple[str, str]:
    """
    Validate uploaded media file extension and MIME type.
    Returns (file_type: 'video'|'audio', sanitized_filename).
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename.")

    clean_filename = sanitize_filename(file.filename)
    ext = Path(clean_filename).suffix.lower()

    if ext in settings.allowed_video_extensions:
        file_type = "video"
    elif ext in settings.allowed_audio_extensions:
        file_type = "audio"
    else:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file format '{ext}'. Allowed video: "
                f"{', '.join(settings.allowed_video_extensions)}; "
                f"Allowed audio: {', '.join(settings.allowed_audio_extensions)}"
            ),
        )

    return file_type, clean_filename


def validate_document_file(file: UploadFile) -> str:
    """Validate supporting document extension."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Document file has no filename.")

    clean_filename = sanitize_filename(file.filename)
    ext = Path(clean_filename).suffix.lower()

    if ext not in settings.allowed_document_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported document format '{ext}'. Allowed: {', '.join(settings.allowed_document_extensions)}",
        )
    return clean_filename


async def save_upload_file(upload_file: UploadFile, destination_path: str, max_size_mb: int) -> int:
    """Save uploaded stream to disk while enforcing max file size."""
    max_bytes = max_size_mb * 1024 * 1024
    total_bytes = 0

    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    with open(destination_path, "wb") as buffer:
        while chunk := await upload_file.read(1024 * 1024):  # 1MB chunks
            total_bytes += len(chunk)
            if total_bytes > max_bytes:
                buffer.close()
                if os.path.exists(destination_path):
                    os.remove(destination_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds maximum allowed size of {max_size_mb} MB.",
                )
            buffer.write(chunk)

    return total_bytes


def extract_audio_from_video(video_path: str, output_wav_path: str) -> bool:
    """
    Extract audio track from video as 16kHz mono WAV using ffmpeg.
    Returns True if audio extracted, False if failed/no audio stream.
    """
    os.makedirs(os.path.dirname(output_wav_path), exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        output_wav_path,
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if res.returncode == 0 and os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 0:
            return True
        logger.warning("FFmpeg audio extraction exited with code", code=res.returncode, err=res.stderr.decode(errors="ignore")[:300])
        return False
    except Exception as exc:
        logger.warning("Audio extraction failed", error=str(exc))
        return False


def analyze_video_opencv(video_path: str, session_id: str) -> dict[str, Any]:
    """
    Analyze video with OpenCV:
    - FPS, resolution, total duration, frame count.
    - Scene change and slide transition detection.
    - Save extracted representative keyframes.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.warning("OpenCV could not open video file", video_path=video_path)
        return {
            "duration_seconds": 0.0,
            "keyframes": [],
            "scene_changes": 0,
            "visual_activity": 0.0,
            "fps": 0.0,
            "resolution": "N/A",
        }

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    duration_seconds = total_frames / fps if fps > 0 else 0.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    keyframes_dir = os.path.join(settings.keyframes_dir, session_id)
    os.makedirs(keyframes_dir, exist_ok=True)

    keyframes = []
    scene_changes = 0
    prev_gray = None

    # Sample rate: sample 1 frame per second to analyze transitions
    step = max(1, int(fps))
    curr_frame_idx = 0
    last_saved_time = -10.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if curr_frame_idx % step == 0:
            timestamp = round(curr_frame_idx / fps, 2)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (160, 90))

            is_transition = False
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                change_ratio = float(diff.mean())
                # Threshold for visual scene/slide change
                if change_ratio > 18.0:
                    scene_changes += 1
                    is_transition = True
            else:
                # First frame is always a keyframe
                is_transition = True

            # Save keyframe across the video timeline, up to 10 keyframes
            min_kf_interval = max(3.0, duration_seconds / 10.0) if duration_seconds > 30 else 3.0
            if (is_transition or len(keyframes) == 0) and (timestamp - last_saved_time >= min_kf_interval) and len(keyframes) < 10:
                keyframe_filename = f"kf_{int(timestamp)}s.jpg"
                keyframe_disk_path = os.path.join(keyframes_dir, keyframe_filename)
                cv2.imwrite(keyframe_disk_path, frame)
                keyframes.append({
                    "timestamp": timestamp,
                    "path": keyframe_disk_path,
                    "url": f"/static/keyframes/{session_id}/{keyframe_filename}",
                    "label": f"Visual Shift at {int(timestamp // 60):02d}:{int(timestamp % 60):02d}",
                })
                last_saved_time = timestamp

            prev_gray = gray

        curr_frame_idx += 1

    cap.release()

    # Visual activity score (0 - 100%)
    sampled_count = max(1, total_frames // step)
    visual_activity = min(100.0, round((scene_changes / sampled_count) * 100.0, 1))

    return {
        "duration_seconds": round(duration_seconds, 2),
        "keyframes": keyframes,
        "scene_changes": scene_changes,
        "visual_activity": visual_activity,
        "fps": round(fps, 1),
        "resolution": f"{width}x{height}",
    }


def extract_document_structure(doc_path: str) -> dict[str, Any]:
    """
    Extract structured pages/slides from PDF, PPTX, or TXT document.
    Returns:
    {
        "document_name": str,
        "total_pages": int,
        "pages": [{"page_number": int, "title": str, "content": str}],
        "full_text": str,
        "summary": str
    }
    """
    ext = Path(doc_path).suffix.lower()
    doc_name = Path(doc_path).name
    pages: list[dict[str, Any]] = []
    full_text = ""

    try:
        if ext == ".pdf":
            import pdfplumber
            with pdfplumber.open(doc_path) as pdf:
                for idx, page in enumerate(pdf.pages, start=1):
                    p_text = (page.extract_text() or "").strip()
                    first_line = p_text.split("\n")[0][:60] if p_text else f"Page {idx}"
                    pages.append({
                        "page_number": idx,
                        "title": first_line,
                        "content": p_text,
                    })
                full_text = "\n\n".join(p["content"] for p in pages if p["content"])

        elif ext in [".pptx", ".ppt"]:
            from pptx import Presentation
            prs = Presentation(doc_path)
            for idx, slide in enumerate(prs.slides, start=1):
                slide_texts = []
                for shape in slide.shapes:
                    if shape.has_text_frame and shape.text.strip():
                        slide_texts.append(shape.text.strip())
                content = "\n".join(slide_texts)
                title = slide_texts[0][:60] if slide_texts else f"Slide {idx}"
                pages.append({
                    "page_number": idx,
                    "title": title,
                    "content": content,
                })
            full_text = "\n\n".join(p["content"] for p in pages if p["content"])

        elif ext == ".txt":
            with open(doc_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read().strip()
            # Split sections by blank lines or headers
            sections = [s.strip() for s in re.split(r"\n\s*\n", raw_text) if s.strip()]
            if not sections:
                sections = [raw_text] if raw_text else []
            for idx, sec in enumerate(sections, start=1):
                first_line = sec.split("\n")[0][:60]
                pages.append({
                    "page_number": idx,
                    "title": first_line or f"Section {idx}",
                    "content": sec,
                })
            full_text = raw_text

    except Exception as exc:
        logger.warning("Document structure extraction failed", error=str(exc), path=doc_path)

    summary_preview = full_text[:200].replace("\n", " ").strip()
    return {
        "document_name": doc_name,
        "total_pages": len(pages),
        "pages": pages,
        "full_text": full_text.strip(),
        "summary": summary_preview,
    }


def extract_document_text(doc_path: str) -> str:
    """Extract text from PDF, PPTX, or TXT document."""
    structure = extract_document_structure(doc_path)
    return structure.get("full_text", "")
