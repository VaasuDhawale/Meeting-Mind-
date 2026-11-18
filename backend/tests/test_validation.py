"""
Validation & Error Handling Tests for VideoIntel API.
Tests unsupported files, missing files, invalid payload parameters.
"""

import io
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Verify health check returns healthy."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "database" in data


@pytest.mark.asyncio
async def test_unsupported_file_extension():
    """Verify backend rejects unsupported executable/archive formats."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("malicious_test.exe", io.BytesIO(b"MZ\x90\x00"), "application/x-msdownload"),
        }
        data = {"title": "Test Malicious Upload"}
        response = await client.post("/api/v1/sessions/analyze", data=data, files=files)
        assert response.status_code == 400
        assert "Unsupported file format '.exe'" in response.json()["detail"]


@pytest.mark.asyncio
async def test_unsupported_document_extension():
    """Verify backend rejects unsupported document types."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("valid_audio.wav", io.BytesIO(b"RIFF....WAVEfmt "), "audio/wav"),
            "document": ("bad_script.bat", io.BytesIO(b"echo off"), "text/plain"),
        }
        data = {"title": "Test Bad Document"}
        response = await client.post("/api/v1/sessions/analyze", data=data, files=files)
        assert response.status_code == 400
        assert "Unsupported document format '.bat'" in response.json()["detail"]


@pytest.mark.asyncio
async def test_missing_file_payload():
    """Verify backend rejects request without media file."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        data = {"title": "No File Provided"}
        response = await client.post("/api/v1/sessions/analyze", data=data)
        assert response.status_code == 422  # Unprocessable Entity (FastAPI validation)


@pytest.mark.asyncio
async def test_get_nonexistent_session():
    """Verify 404 for invalid UUID lookup."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/sessions/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert response.json()["detail"] == "Meeting session not found"
