"""
End-to-End Pipeline Tests for MeetingMind.
Tests the full multimodal session processing, PDF generation, and persistence.
"""

import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_faculty_demo_full_pipeline():
    """Verify complete faculty demo pipeline executes end to end."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Trigger demo
        response = await client.post("/api/v1/sessions/demo")
        assert response.status_code == 200
        session = response.json()

        # 2. Check schema and intelligence outputs
        assert session["status"] == "completed"
        assert session["id"] is not None
        assert "Faculty Demo" in session["title"]
        assert len(session["summary"]) > 50
        assert len(session["action_items"]) >= 2
        assert len(session["decisions"]) >= 1
        assert len(session["topics"]) >= 1
        assert "positive_score" in session["sentiment"]
        assert session["has_pdf"] is True

        session_id = session["id"]

        # 3. Verify PDF download
        pdf_resp = await client.get(f"/api/v1/sessions/{session_id}/pdf")
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert pdf_resp.content.startswith(b"%PDF")

        # 4. Verify list endpoint contains session
        list_resp = await client.get("/api/v1/sessions")
        assert list_resp.status_code == 200
        sessions = list_resp.json()
        assert any(s["id"] == session_id for s in sessions)
