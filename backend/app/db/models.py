"""
SQLAlchemy database models for Video & Meeting Intelligence.
"""

from datetime import datetime, timezone
import uuid
from typing import Any

from sqlalchemy import Column, String, Text, Float, DateTime, JSON
from app.db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class MeetingSession(Base):
    """Stores meeting intelligence sessions and multimodal analysis results."""

    __tablename__ = "meeting_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="Untitled Meeting")
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Media metadata
    source_filename = Column(String(255), nullable=True)
    source_file_type = Column(String(50), nullable=True)  # video, audio
    file_path = Column(String(500), nullable=True)
    duration_seconds = Column(Float, default=0.0)

    # Document attachment
    document_filename = Column(String(255), nullable=True)
    document_path = Column(String(500), nullable=True)

    # AI Intelligence Results
    ai_provider = Column(String(50), default="local_ml")
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    action_items = Column(JSON, default=list)  # [{"task": str, "assignee": str, "priority": str, "due_date": str}]
    decisions = Column(JSON, default=list)     # [str]
    topics = Column(JSON, default=list)        # [{"topic": str, "relevance": float, "keywords": [str]}]
    sentiment = Column(JSON, default=dict)     # {"overall": str, "positive_score": float, "neutral_score": float, "negative_score": float}
    video_analysis = Column(JSON, default=dict) # {"keyframes": [{"timestamp": float, "path": str, "label": str}], "scene_changes": int, "visual_activity": float}
    speakers = Column(JSON, default=list)      # [{"name": str, "speaking_time": float, "percentage": float}]

    # Multimodal & Dynamic Intelligence Extensions
    questions_answers = Column(JSON, default=list) # [{"question": str, "answer": str, "speaker": str, "timestamp": str, "evidence": str}]
    timeline = Column(JSON, default=list)          # [{"timestamp": str, "time_seconds": float, "type": str, "title": str, "description": str, "evidence": str}]
    document_analysis = Column(JSON, default=dict) # {"document_name": str, "total_pages": int, "pages": list, "summary": str}
    evidence = Column(JSON, default=list)          # [{"id": str, "claim_type": str, "claim": str, "source_type": str, "timestamp": str, "quote": str}]

    # Generated Report
    pdf_path = Column(String(500), nullable=True)
    docx_path = Column(String(500), nullable=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary for API response."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "source_filename": self.source_filename,
            "source_file_type": self.source_file_type,
            "duration_seconds": self.duration_seconds,
            "document_filename": self.document_filename,
            "ai_provider": self.ai_provider,
            "transcript": self.transcript,
            "summary": self.summary,
            "action_items": self.action_items or [],
            "decisions": self.decisions or [],
            "topics": self.topics or [],
            "sentiment": self.sentiment or {},
            "video_analysis": self.video_analysis or {},
            "speakers": self.speakers or [],
            "questions_answers": self.questions_answers or [],
            "timeline": self.timeline or [],
            "document_analysis": self.document_analysis or {},
            "evidence": self.evidence or [],
            "has_pdf": bool(self.pdf_path),
            "has_docx": bool(self.docx_path),
            "meeting_overview": (self.video_analysis or {}).get("meeting_overview"),
            "key_discussion_points": (self.video_analysis or {}).get("key_discussion_points", []),
            "open_questions": (self.video_analysis or {}).get("open_questions", []),
            "risks_blockers": (self.video_analysis or {}).get("risks_blockers", []),
            "important_moments": (self.video_analysis or {}).get("important_moments", []),
            "topics_mind_map": (self.video_analysis or {}).get("topics_mind_map", []),
            "transcript_segments": (self.video_analysis or {}).get("transcript_segments", []),
            "transcript_lines": (self.video_analysis or {}).get("transcript_lines", []),
        }
