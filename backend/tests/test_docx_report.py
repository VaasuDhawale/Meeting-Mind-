"""
Tests for Word Document (.docx) Generation, Validation, and Download Endpoint.
"""

import os
import zipfile
import pytest
import docx
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.docx_service import generate_meeting_docx_report


@pytest.fixture
def sample_session_data():
    return {
        "id": "test-docx-fixture-1234",
        "title": "Quarterly Technical Architecture & ML Review",
        "status": "completed",
        "created_at": "2026-10-13T10:00:00Z",
        "source_filename": "architecture_review.mp4",
        "source_file_type": "video",
        "duration_seconds": 185.0,
        "ai_provider": "Local ML Pipeline (TF-IDF & TextRank)",
        "summary": "The team reviewed the multimodal intelligence pipeline including OpenCV scene detection and speech transcription. All milestones were approved.",
        "topics": [
            {"topic": "Multimodal Pipeline", "relevance": 0.95, "keywords": ["OpenCV", "FFmpeg", "Audio"]},
            {"topic": "Document Generation", "relevance": 0.88, "keywords": ["python-docx", "ReportLab", "XML"]},
            {"topic": "Local Fallback", "relevance": 0.82, "keywords": ["Offline", "scikit-learn", "SpeechRecognition"]},
        ],
        "action_items": [
            {
                "task": "Complete automated DOCX validation tests",
                "assignee": "Lead Engineer",
                "priority": "High",
                "due_date": "2026-10-15",
                "status": "completed",
                "evidence": "Transcript [02:15]",
            },
            {
                "task": "Deploy updated backend and frontend endpoints",
                "assignee": "DevOps Team",
                "priority": "Medium",
                "due_date": "2026-10-18",
                "status": "pending",
                "evidence": "Transcript [02:45]",
            },
        ],
        "decisions": [
            {
                "decision": "Adopt python-docx for native editable Microsoft Word report compilation",
                "context": "Allows executive editing and full fidelity",
                "participants": "Alex, Priya, David",
                "timestamp": "01:30",
                "evidence": "We agreed to use python-docx for genuine Word reports",
            }
        ],
        "questions_answers": [
            {
                "question": "Can the generated Word file be opened in Microsoft Word without conversion errors?",
                "answer": "Yes, it generates a standard Office Open XML package.",
                "speaker": "David Chen",
                "evidence": "David: Can it be opened in Word? Alex: Yes.",
            }
        ],
        "timeline": [
            {"timestamp": "00:00", "type": "moment", "title": "Session Kickoff", "evidence": "Alex opens call"},
            {"timestamp": "01:30", "type": "decision", "title": "Format Decision", "evidence": "Agreed on DOCX"},
            {"timestamp": "02:15", "type": "action", "title": "Validation Task", "evidence": "Assigned to Lead"},
        ],
        "video_analysis": {
            "keyframes": [],
            "scene_changes": 4,
            "visual_activity": 18.5,
        },
        "speakers": [
            {"name": "Alex Rivera", "speaking_time": 90.0, "percentage": 50.0},
            {"name": "Priya Sharma", "speaking_time": 50.0, "percentage": 28.0},
            {"name": "David Chen", "speaking_time": 40.0, "percentage": 22.0},
        ],
        "sentiment": {
            "overall": "Positive",
            "positive_score": 0.85,
            "neutral_score": 0.10,
            "negative_score": 0.05,
        },
        "evidence": [
            {
                "id": "ev-1",
                "claim_type": "decision",
                "claim": "Adopt python-docx for native Word reports",
                "source_type": "transcript",
                "timestamp": "01:30",
                "quote": "We agreed to use python-docx for genuine Word reports",
            }
        ],
        "transcript": "Alex Rivera: Welcome everyone.\nPriya Sharma: The OpenCV engine is ready.\nDavid Chen: Can it be opened in Word?\nAlex Rivera: Yes.",
    }


def test_docx_generation_package_integrity(sample_session_data):
    """Verify that generated .docx file is a valid Office Open XML ZIP package."""
    session_id = sample_session_data["id"]
    file_path = generate_meeting_docx_report(sample_session_data, session_id)

    assert os.path.exists(file_path), "Generated file must exist"
    assert file_path.endswith(".docx"), "File extension must be .docx"
    assert os.path.getsize(file_path) > 2000, "File size must be reasonable"

    # ZIP package integrity
    with zipfile.ZipFile(file_path, "r") as zf:
        namelist = zf.namelist()
        assert "word/document.xml" in namelist, "Package must contain word/document.xml"
        assert "[Content_Types].xml" in namelist, "Package must contain [Content_Types].xml"
        assert "_rels/.rels" in namelist, "Package must contain _rels/.rels"


def test_docx_parser_and_content_verification(sample_session_data):
    """Verify that python-docx can reopen the file and verify expected headings and tables."""
    session_id = sample_session_data["id"]
    file_path = generate_meeting_docx_report(sample_session_data, session_id)

    doc = docx.Document(file_path)

    # Check title and headings
    full_text = "\n".join(p.text for p in doc.paragraphs)
    assert sample_session_data["title"] in full_text
    assert "1. Executive Summary" in full_text
    assert "3. Key Discussion Points" in full_text
    assert "4. Topics & Key Concepts" in full_text
    assert "5. Decisions & Agreed Outcomes" in full_text
    assert "6. Action Items & Next Steps" in full_text
    assert "12. Complete Dialogue & Verbatim Transcript" in full_text
    assert "13. Processing Details & Verification Audit" in full_text

    # Check tables
    assert len(doc.tables) >= 4, "Must contain at least metadata, topics, action items, and timeline tables"

    # Check action items table
    table_texts = [" ".join(cell.text for cell in row.cells) for t in doc.tables for row in t.rows]
    combined_table_text = " ".join(table_texts)
    assert "Lead Engineer" in combined_table_text
    assert "Complete automated DOCX validation tests" in combined_table_text
    assert "DevOps Team" in combined_table_text


@pytest.mark.asyncio
async def test_docx_download_endpoint_returns_binary():
    """Verify GET /sessions/{id}/docx returns HTTP 200 with proper MIME type."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Run demo first to create a known session
        demo_res = await client.post("/api/v1/sessions/demo")
        assert demo_res.status_code == 200
        session_id = demo_res.json()["id"]

        # Request the .docx download
        docx_res = await client.get(f"/api/v1/sessions/{session_id}/docx")
        assert docx_res.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in docx_res.headers.get("content-type", "")
        assert "attachment" in docx_res.headers.get("content-disposition", "")
        assert ".docx" in docx_res.headers.get("content-disposition", "")
        assert len(docx_res.content) > 1000

        # Verify the returned bytes form a valid docx
        import io
        docx_bytes = io.BytesIO(docx_res.content)
        with zipfile.ZipFile(docx_bytes, "r") as zf:
            assert "word/document.xml" in zf.namelist()


@pytest.mark.asyncio
async def test_docx_download_missing_session_returns_404():
    """Verify GET /sessions/{invalid-id}/docx returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/sessions/non-existent-session-id/docx")
        assert res.status_code == 404
