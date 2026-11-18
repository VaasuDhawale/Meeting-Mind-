"""
Dynamic Report Engine & Multi-Format Export Test Suite.
Tests dynamic section selection (A through G), PDF validity, JSON and Markdown consistency.
"""

import os
import re
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.report_engine import (
    build_dynamic_report,
    generate_json_export,
    generate_markdown_report,
)
from app.services.pdf_service import generate_meeting_pdf_report


def test_scenario_a_full_session():
    """TEST A: Session containing summary + topics + tasks + decisions."""
    data = {
        "id": "test-a",
        "title": "Complete Architecture Sync",
        "summary": "The executive board finalized the quarterly delivery milestones.",
        "topics": [{"topic": "Architecture", "relevance": 0.9, "keywords": ["system"]}],
        "action_items": [{"task": "Deploy backend service", "assignee": "Alex", "priority": "High", "due_date": "Friday"}],
        "decisions": [{"decision": "Adopt PostgreSQL and Redis", "context": "Infrastructure", "participants": "Alex"}],
        "source_file_type": "video",
        "duration_seconds": 120.0,
    }
    report = build_dynamic_report(data)
    assert report["has_summary"] is True
    assert report["has_topics"] is True
    assert report["has_actions"] is True
    assert report["has_decisions"] is True
    assert "executive_summary" in report["active_sections"]
    assert "topics" in report["active_sections"]
    assert "action_items" in report["active_sections"]
    assert "decisions" in report["active_sections"]


def test_scenario_b_no_decisions():
    """TEST B: Session with no decisions — verifies decisions section is omitted."""
    data = {
        "id": "test-b",
        "title": "Informational Standup",
        "summary": "Team shared current work in progress without making formal decisions.",
        "topics": [{"topic": "Updates", "relevance": 0.8, "keywords": ["standup"]}],
        "action_items": [{"task": "Review pull request #42", "assignee": "David", "priority": "Medium", "due_date": "Today"}],
        "decisions": [],  # No decisions
        "duration_seconds": 60.0,
    }
    report = build_dynamic_report(data)
    assert report["has_decisions"] is False
    assert "decisions" not in report["active_sections"]
    md = generate_markdown_report(data)
    assert "Formal Decisions & Agreements" not in md
    json_exp = generate_json_export(data)
    assert len(json_exp["decisions"]) == 0


def test_scenario_c_no_action_items():
    """TEST C: Session with no action items — verifies action items section is omitted."""
    data = {
        "id": "test-c",
        "title": "Retrospective Review",
        "summary": "Reviewed sprint outcomes without scheduling new action items.",
        "topics": [{"topic": "Sprint Review", "relevance": 0.85, "keywords": ["sprint"]}],
        "action_items": [],  # No action items
        "decisions": ["Concluded that current sprint velocity meets quarterly target"],
        "duration_seconds": 90.0,
    }
    report = build_dynamic_report(data)
    assert report["has_actions"] is False
    assert "action_items" not in report["active_sections"]
    md = generate_markdown_report(data)
    assert "Action Items & Deliverables" not in md
    json_exp = generate_json_export(data)
    assert len(json_exp["action_items"]) == 0


def test_scenario_d_document_analysis():
    """TEST D: Session containing PPT/PDF document analysis."""
    data = {
        "id": "test-d",
        "title": "Slide Presentation Sync",
        "summary": "Reviewed architecture slides.",
        "document_filename": "architecture_deck.pptx",
        "document_analysis": {
            "document_name": "architecture_deck.pptx",
            "total_pages": 3,
            "pages": [
                {"page_number": 1, "title": "System Overview", "content": "Microservices diagram", "spoken_alignment": "Alex explained the diagram"},
            ],
        },
        "duration_seconds": 180.0,
    }
    report = build_dynamic_report(data)
    assert report["has_document"] is True
    assert "document_analysis" in report["active_sections"]
    md = generate_markdown_report(data)
    assert "Document & Slide Analysis" in md


def test_scenario_e_visual_evidence():
    """TEST E: Session containing visual evidence from OpenCV."""
    data = {
        "id": "test-e",
        "title": "Screen Share Demo",
        "summary": "Live UI demonstration.",
        "source_file_type": "video",
        "video_analysis": {
            "scene_changes": 4,
            "visual_activity": 35.5,
            "keyframes": [
                {"timestamp": 2.5, "url": "/static/kf1.jpg", "label": "Slide Change at 00:02"},
            ],
        },
        "duration_seconds": 60.0,
    }
    report = build_dynamic_report(data)
    assert report["has_visual"] is True
    assert "visual_intelligence" in report["active_sections"]
    md = generate_markdown_report(data)
    assert "OpenCV Visual Intelligence" in md


def test_scenario_f_speaker_data():
    """TEST F: Session with real speaker data vs without diarization."""
    # With speakers
    data_with_spk = {
        "id": "test-f1",
        "title": "Panel Discussion",
        "summary": "Interactive dialogue.",
        "speakers": [
            {"name": "Dr. Smith", "speaking_time": 45.0, "turns": 4, "percentage": 60.0},
            {"name": "Alex", "speaking_time": 30.0, "turns": 2, "percentage": 40.0},
        ],
        "duration_seconds": 75.0,
    }
    report_spk = build_dynamic_report(data_with_spk)
    assert report_spk["has_speakers"] is True
    assert len(report_spk["speakers"]) == 2

    # Without speakers
    data_no_spk = {
        "id": "test-f2",
        "title": "Solo Monologue",
        "summary": "Single speaker lecture.",
        "speakers": [],
        "transcript": "Hello everyone welcome to lecture 1.",
        "duration_seconds": 75.0,
    }
    report_no_spk = build_dynamic_report(data_no_spk)
    assert report_no_spk["has_speakers"] is False


def test_scenario_g_multilingual_text():
    """TEST G: Multilingual text support without crashes."""
    data = {
        "id": "test-g",
        "title": "Multilingual Global Sync: 東京 & München",
        "summary": "Discuté des jalons avec les équipes de Tokyo (東京) et Munich.",
        "topics": [{"topic": "Global Deployment (東京)", "relevance": 0.9, "keywords": ["東京", "Tokyo"]}],
        "decisions": ["Approuvé: déploiement global prévu pour le prochain trimestre."],
        "action_items": [{"task": "Tester la localisation française et japonaise", "assignee": "Jean-Luc", "priority": "High", "due_date": "Demain"}],
        "duration_seconds": 120.0,
    }
    report = build_dynamic_report(data)
    assert report["has_summary"] is True
    pdf_path = generate_meeting_pdf_report(data, "test-g")
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000


@pytest.mark.asyncio
async def test_end_to_end_demo_exports():
    """
    End-to-end verification:
    DEMO INPUT → PROCESSING → DYNAMIC REPORT → PDF, JSON, MARKDOWN EXPORTS.
    Verifies data consistency across all outputs.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Trigger faculty demo
        resp = await client.post("/api/v1/sessions/demo")
        assert resp.status_code == 200
        session = resp.json()
        session_id = session["id"]

        # 2. Check structured outputs
        assert session["status"] == "completed"
        assert len(session["summary"]) > 30
        assert len(session["action_items"]) >= 1
        assert len(session["decisions"]) >= 1
        assert len(session["topics"]) >= 1
        assert session["has_pdf"] is True

        # 3. Test JSON Export endpoint
        json_resp = await client.get(f"/api/v1/sessions/{session_id}/json")
        assert json_resp.status_code == 200
        json_data = json_resp.json()
        assert "session" in json_data
        assert "summary" in json_data
        assert len(json_data["action_items"]) == len(session["action_items"])
        assert len(json_data["decisions"]) == len(session["decisions"])

        # 4. Test Markdown Export endpoint
        md_resp = await client.get(f"/api/v1/sessions/{session_id}/markdown")
        assert md_resp.status_code == 200
        assert md_resp.headers["content-type"].startswith("text/markdown")
        assert "Executive Summary" in md_resp.text
        assert "Formal Decisions" in md_resp.text

        # 5. Test Plain Text Export endpoint
        txt_resp = await client.get(f"/api/v1/sessions/{session_id}/txt")
        assert txt_resp.status_code == 200
        assert txt_resp.headers["content-type"].startswith("text/plain")

        # 6. Test PDF Download endpoint & binary header validation
        pdf_resp = await client.get(f"/api/v1/sessions/{session_id}/pdf")
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert pdf_resp.content.startswith(b"%PDF")
        assert len(pdf_resp.content) > 3000  # Valid non-trivial PDF


def test_educational_session_extraction():
    """Verify that educational sessions do not fabricate business action items or corporate decisions."""
    from app.services.nlp_ai_service import run_local_ml_pipeline
    sample_text = (
        "Wake up, everybody! I'm a live-in kickin'. Open up, my emergency beats yours! "
        "I love sports! Where's my coffee? Again? No, more coffee! Stay awake! "
        "I'm so sick of them getting wasted every night, will they ever quit?"
    )
    segments = [
        {"start": 12.0, "end": 14.0, "timestamp": "00:12", "text": "Wake up, everybody!"},
        {"start": 42.0, "end": 45.0, "timestamp": "00:42", "text": "My emergency beats yours!"},
        {"start": 86.0, "end": 89.0, "timestamp": "01:26", "text": "More coffee! Stay awake!"},
        {"start": 108.0, "end": 110.0, "timestamp": "01:48", "text": "Will they ever quit?"},
    ]
    meta = {"duration_seconds": 122.0, "keyframes": [], "scene_changes": 12, "visual_activity": 45.0}

    results = run_local_ml_pipeline(
        combined_text=sample_text,
        video_metadata=meta,
        transcript_segments=segments,
        session_title="Daily Life of Human Organs (Organismo)",
    )

    # 1. Session type must be educational
    assert results["session_type"] == "educational_video"

    # 2. Never fabricate action items or decisions for educational video
    assert len(results["action_items"]) == 0
    assert len(results["decisions"]) == 0

    # 3. Key points must have relative timestamps formatted as MM:SS
    assert len(results["key_discussion_points"]) > 0
    for pt in results["key_discussion_points"]:
        assert re.search(r"\(\d{2}:\d{2}\)", pt["formatted"])

    # 4. Open questions and risks must be grounded
    assert any("wasted" in q["question"].lower() for q in results["open_questions"])
    assert any("alcohol" in r["risk"].lower() or "liver" in r["risk"].lower() or "sleep" in r["risk"].lower() for r in results["risks_blockers"])

    # 5. Build dynamic report and test PDF generation
    report_dict = {
        "id": "edu-test-session",
        "title": "Daily Life of Human Organs (Organismo)",
        "summary": results["summary"],
        "meeting_overview": results["meeting_overview"],
        "key_discussion_points": results["key_discussion_points"],
        "action_items": results["action_items"],
        "decisions": results["decisions"],
        "open_questions": results["open_questions"],
        "risks_blockers": results["risks_blockers"],
        "important_moments": results["important_moments"],
        "topics_mind_map": results["topics_mind_map"],
        "transcript_lines": results["transcript_lines"],
        "transcript_segments": segments,
        "video_analysis": meta,
        "duration_seconds": 122.0,
        "source_file_type": "video",
    }
    pdf_path = generate_meeting_pdf_report(report_dict, "edu-test-session")
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 3000

