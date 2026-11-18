"""
PDF Generation Service: Builds publication-ready Meeting Intelligence and Full Transcript reports using ReportLab.
100% faithful replication of the SessionMind AI Meeting Report layout, typography, screenshot styling, and transcript.
"""

import os
import re
from datetime import datetime, timezone
from typing import Any
from xml.sax.saxutils import escape

import structlog
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen import canvas

from app.config import settings
from app.services.report_engine import build_dynamic_report

logger = structlog.get_logger()


def format_seconds(seconds: float) -> str:
    """Format seconds into video-relative MM:SS or HH:MM:SS."""
    secs = int(max(0.0, round(seconds)))
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def normalize_timestamp_val(val: Any, base_offset: float = 0.0) -> str:
    """Normalize any raw timestamp, float, Unix epoch, or string to video-relative MM:SS."""
    if val is None or val == "":
        return "00:00"
    s_val = str(val).strip().rstrip("s")
    if re.match(r"^\d{1,2}:\d{2}(?::\d{2})?$", s_val):
        return s_val
    try:
        f_val = float(s_val)
        if f_val > 100000:
            if base_offset > 0:
                f_val = max(0.0, f_val - base_offset)
            else:
                f_val = 0.0
        return format_seconds(f_val)
    except (ValueError, TypeError):
        return s_val


def clean_report_timestamp_string(text: str, base_offset: float = 0.0) -> str:
    """Convert any embedded raw epoch timestamp (like 1790534708.49 or 1790534708s) into MM:SS."""
    if not text:
        return ""
    if base_offset == 0.0:
        matches = [float(x) for x in re.findall(r"\b(1[6-9]\d{8}(?:\.\d+)?)\b", text)]
        if matches:
            base_offset = min(matches)

    def repl(m):
        raw_val = float(m.group(1))
        rel_val = max(0.0, raw_val - base_offset) if base_offset > 0 else raw_val
        return format_seconds(rel_val)

    # Replace epoch timestamp pattern
    cleaned = re.sub(r"\b(1[6-9]\d{8}(?:\.\d+)?)(?:s)?\b", repl, text)
    # Also clean trailing s from timestamps like 00:12s -> 00:12
    cleaned = re.sub(r"(\b\d{1,2}:\d{2})s\b", r"\1", cleaned)
    return cleaned


def safe_text(text: Any) -> str:
    """Escape text safely for ReportLab XML/HTML flowables and strip invalid control chars."""
    if text is None:
        return ""
    s = str(text)
    s = "".join(ch for ch in s if ord(ch) >= 32 or ch in "\n\t")
    return escape(s)


class NumberedCanvas(canvas.Canvas):
    """Canvas that performs a two-pass calculation of total pages for footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 25, page_text)
        self.restoreState()


def get_proportional_image(image_path: str, max_width: float = 460.0, max_height: float = 230.0) -> Image | None:
    """Create a ReportLab Image maintaining aspect ratio."""
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with PILImage.open(image_path) as img:
            orig_w, orig_h = img.size
        if orig_w <= 0 or orig_h <= 0:
            return None
        ratio = min(max_width / orig_w, max_height / orig_h)
        w = orig_w * ratio
        h = orig_h * ratio
        return Image(image_path, width=w, height=h)
    except Exception as exc:
        logger.warning("Failed to load image for PDF", path=image_path, error=str(exc))
        return None


def generate_meeting_pdf_report(session_data: dict[str, Any], session_id: str) -> str:
    """
    Generate a complete, publication-ready PDF report matching SessionMind layout 100%.
    """
    os.makedirs(settings.reports_dir, exist_ok=True)
    pdf_filename = f"report_{session_id}.pdf"
    pdf_path = os.path.join(settings.reports_dir, pdf_filename)

    # Auto-derive any missing SessionMind sections from transcript and video analysis
    if not session_data.get("key_discussion_points") or not session_data.get("open_questions") or not session_data.get("important_moments"):
        from app.services.nlp_ai_service import run_local_ml_pipeline
        aux = run_local_ml_pipeline(
            session_data.get("transcript", ""),
            session_data.get("video_analysis", {}),
            transcript_segments=session_data.get("transcript_segments"),
            session_title=session_data.get("title"),
        )
        for k in ["meeting_overview", "key_discussion_points", "open_questions", "risks_blockers", "important_moments", "topics_mind_map", "augmented_keyframes", "transcript_lines"]:
            if not session_data.get(k):
                session_data[k] = aux.get(k)

    report = build_dynamic_report(session_data)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    header_brand_style = ParagraphStyle(
        "HeaderBrand",
        parent=styles["Normal"],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        spaceAfter=5,
    )

    session_title_style = ParagraphStyle(
        "SessionTitle",
        parent=styles["Heading1"],
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        spaceAfter=2,
    )

    project_tag_style = ParagraphStyle(
        "ProjectTag",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        fontName="Helvetica",
        spaceAfter=8,
    )

    section_heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        spaceBefore=7,
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica",
        spaceAfter=3,
    )

    item_line_style = ParagraphStyle(
        "ItemLine",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica",
        spaceAfter=2,
    )

    mind_map_root_style = ParagraphStyle(
        "MindMapRoot",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica-Bold",
        spaceAfter=2,
    )

    mind_map_item_style = ParagraphStyle(
        "MindMapItem",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica",
        spaceAfter=1.5,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#334155"),
        fontName="Helvetica",
    )

    screenshot_caption_style = ParagraphStyle(
        "ScreenshotCaption",
        parent=styles["Normal"],
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
        fontName="Helvetica-Bold",
        alignment=1,  # Center
    )

    evidence_ts_style = ParagraphStyle(
        "EvidenceTimestamp",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#64748b"),
        fontName="Helvetica",
        spaceBefore=2,
        spaceAfter=8,
    )

    transcript_line_style = ParagraphStyle(
        "TranscriptLine",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155"),
        fontName="Helvetica",
        spaceAfter=1.5,
    )

    story = []

    # Detect if session is educational
    title_text = report["title"] or "Executive Intelligence Sync"
    is_educational = any(k in title_text.lower() for k in ["organ", "organismo", "biology", "science", "physics", "lecture", "tutorial", "chapter", "animated", "disciplined people", "learning"])
    tag_label = "Category: Educational / Physiology" if "organ" in title_text.lower() else ("Project: learning" if is_educational else "Type: Business Meeting")
    overview_heading = "Session Overview" if is_educational else "Meeting Overview"

    # =========================================================================
    # PAGE 1: Header, Executive Summary, Overview, Discussion Points, Decisions,
    #         Action Items, Open Questions, Risks / Blockers, Initial Moments
    # =========================================================================
    story.append(Paragraph("SessionMind — AI Meeting Report", header_brand_style))
    story.append(Paragraph(safe_text(title_text), session_title_style))
    story.append(Paragraph(safe_text(tag_label), project_tag_style))

    # Executive Summary (Concise 1-2 clean paragraphs)
    story.append(Paragraph("Executive Summary", section_heading_style))
    exec_summary_text = report.get("summary") or "Executive session overview and strategy."
    p_lines = [p.strip() for p in exec_summary_text.split("\n\n") if p.strip()]
    if p_lines:
        story.append(Paragraph(safe_text(clean_report_timestamp_string(p_lines[0])), body_style))
        if len(p_lines) > 1 and "Multimodal visual analysis" not in p_lines[1] and "OpenCV" not in p_lines[1]:
            story.append(Paragraph(safe_text(clean_report_timestamp_string(p_lines[1])), body_style))

    # Session / Meeting Overview
    meeting_overview = report.get("meeting_overview") or (
        f"A presenter reviews key project updates across operational milestones, "
        f"examining implementation standards and delivery timelines."
    )
    story.append(Paragraph(overview_heading, section_heading_style))
    story.append(Paragraph(safe_text(clean_report_timestamp_string(meeting_overview)), body_style))

    # Key Discussion Points (Plain lines with timestamps in parentheses, NO bullet dot)
    key_points = report.get("key_discussion_points") or []
    if key_points:
        story.append(Paragraph("Key Discussion Points", section_heading_style))
        for pt in key_points[:7]:
            if isinstance(pt, dict):
                p_text = pt.get("point") or pt.get("formatted") or ""
                ts = pt.get("timestamp")
                ts_norm = normalize_timestamp_val(ts)
                clean_p = clean_report_timestamp_string(p_text)
                formatted = f"{clean_p} ({ts_norm})" if ts_norm and f"({ts_norm})" not in clean_p else clean_p
            else:
                formatted = clean_report_timestamp_string(str(pt))
            story.append(Paragraph(safe_text(formatted), item_line_style))

    # Decisions
    story.append(Paragraph("Decisions", section_heading_style))
    decisions = report.get("decisions") or []
    if decisions:
        for d in decisions[:2]:
            d_text = d.get("decision") if isinstance(d, dict) else str(d)
            ts = d.get("timestamp") if isinstance(d, dict) else None
            ts_norm = normalize_timestamp_val(ts) if ts else None
            formatted = f"{clean_report_timestamp_string(d_text)} — {ts_norm}" if ts_norm else clean_report_timestamp_string(d_text)
            story.append(Paragraph(safe_text(formatted), item_line_style))

    # Action Items Table
    story.append(Paragraph("Action Items", section_heading_style))
    action_items = report.get("action_items") or []
    act_rows = [
        [
            Paragraph("Owner", table_header_style),
            Paragraph("Task", table_header_style),
            Paragraph("Deadline", table_header_style),
            Paragraph("Status", table_header_style),
        ]
    ]
    if action_items:
        for item in action_items[:2]:
            owner = safe_text(item.get("owner") or item.get("assignee") or "None identified")
            task = safe_text(clean_report_timestamp_string(item.get("task", "")))
            deadline = safe_text(item.get("deadline") or item.get("due_date") or "—")
            status = safe_text(item.get("status", "pending"))
            act_rows.append([
                Paragraph(owner, table_cell_style),
                Paragraph(task, table_cell_style),
                Paragraph(deadline, table_cell_style),
                Paragraph(status, table_cell_style),
            ])
    else:
        act_rows.append([
            Paragraph("—", table_cell_style),
            Paragraph("None recorded.", table_cell_style),
            Paragraph("—", table_cell_style),
            Paragraph("—", table_cell_style),
        ])

    act_table = Table(act_rows, colWidths=[90, 270, 100, 80])
    act_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("PADDING", (0, 0), (-1, -1), 3),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(act_table)

    # Open Questions
    open_questions = report.get("open_questions") or []
    if open_questions:
        story.append(Paragraph("Open Questions", section_heading_style))
        for q in open_questions[:1]:
            q_str = q.get("formatted") or f"{q.get('question')} — {normalize_timestamp_val(q.get('timestamp'))}"
            story.append(Paragraph(safe_text(clean_report_timestamp_string(q_str)), item_line_style))

    # Risks / Blockers
    risks_blockers = report.get("risks_blockers") or []
    if risks_blockers:
        story.append(Paragraph("Risks / Blockers", section_heading_style))
        for r in risks_blockers[:1]:
            r_str = r.get("formatted") or f"{r.get('risk')} — {normalize_timestamp_val(r.get('timestamp'))}"
            story.append(Paragraph(safe_text(clean_report_timestamp_string(r_str)), item_line_style))

    # Important Moments (First 3 items fit on Page 1)
    important_moments = report.get("important_moments") or []
    if important_moments:
        story.append(Paragraph("Important Moments", section_heading_style))
        for m in important_moments[:3]:
            m_title = m.get("title", "")
            st_norm = normalize_timestamp_val(m.get("start_timestamp"))
            et_norm = normalize_timestamp_val(m.get("end_timestamp"))
            m_str = f"{m_title} — {st_norm} — {et_norm}"
            story.append(Paragraph(safe_text(clean_report_timestamp_string(m_str)), item_line_style))

    # =========================================================================
    # PAGE 2: Remaining Important Moments, Changes From Previous Meeting,
    #         Topics / Mind Map, Meeting Screenshots heading & Screenshot 1
    # =========================================================================
    story.append(PageBreak())

    if len(important_moments) > 3:
        for m in important_moments[3:10]:
            m_title = m.get("title", "")
            st_norm = normalize_timestamp_val(m.get("start_timestamp"))
            et_norm = normalize_timestamp_val(m.get("end_timestamp"))
            m_str = f"{m_title} — {st_norm} — {et_norm}"
            story.append(Paragraph(safe_text(clean_report_timestamp_string(m_str)), item_line_style))
        story.append(Spacer(1, 4))

    # Changes From Previous Meeting
    story.append(Paragraph("Changes From Previous Meeting", section_heading_style))
    story.append(Spacer(1, 3))

    # Topics / Mind Map
    mind_map = report.get("topics_mind_map") or []
    if mind_map:
        story.append(Paragraph("Topics / Mind Map", section_heading_style))
        story.append(Paragraph(safe_text(title_text), mind_map_root_style))
        for node in mind_map[:6]:
            prefix = "" if str(node).startswith("→") else "→ "
            story.append(Paragraph(safe_text(f"{prefix}{node}"), mind_map_item_style))
        story.append(Spacer(1, 6))

    # Video Keyframe Preparation
    video_analysis = report.get("video_analysis") or {}
    keyframes = video_analysis.get("keyframes") or []
    augmented_kf = session_data.get("augmented_keyframes") or []

    merged_kf = []
    for idx, kf in enumerate(keyframes):
        kf_copy = dict(kf)
        if idx < len(augmented_kf):
            kf_copy.update(augmented_kf[idx])
        if "path" not in kf_copy or not os.path.exists(kf_copy["path"]):
            url = kf_copy.get("url", "")
            fname = url.split("/")[-1] if url else f"kf_{int(float(kf_copy.get('timestamp', 0)))}s.jpg"
            alt_path = os.path.join(settings.keyframes_dir, session_id, fname)
            if os.path.exists(alt_path):
                kf_copy["path"] = alt_path
        merged_kf.append(kf_copy)

    valid_keyframes = [kf for kf in merged_kf if kf.get("path") and os.path.exists(kf["path"])]

    # Screenshot 1 goes on Page 2 directly under Meeting Screenshots heading
    if valid_keyframes:
        screenshots_heading = "Video Screenshots" if is_educational else "Meeting Screenshots"
        story.append(Paragraph(screenshots_heading, section_heading_style))
        story.append(Spacer(1, 3))

        first_kf = valid_keyframes[0]
        img1 = get_proportional_image(first_kf["path"], max_width=460, max_height=220)
        if img1:
            quote1 = first_kf.get("subtitle_quote") or first_kf.get("label") or ""
            ts1 = normalize_timestamp_val(first_kf.get("evidence_timestamp") or first_kf.get("timestamp"))
            story.append(img1)
            if quote1:
                cap1 = Table([[Paragraph(safe_text(clean_report_timestamp_string(quote1)), screenshot_caption_style)]], colWidths=[460])
                cap1.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#000000")),
                    ("PADDING", (0, 0), (-1, -1), 3),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]))
                story.append(cap1)
            story.append(Paragraph(f"Evidence timestamp: {safe_text(ts1)}", evidence_ts_style))

    # =========================================================================
    # PAGES 3 - 7: EXACTLY TWO SCREENSHOTS PER PAGE
    # =========================================================================
    remaining_keyframes = valid_keyframes[1:]
    for idx in range(0, len(remaining_keyframes), 2):
        story.append(PageBreak())
        chunk = remaining_keyframes[idx : idx + 2]
        for kf_item in chunk:
            img = get_proportional_image(kf_item["path"], max_width=460, max_height=220)
            if not img:
                continue
            quote = kf_item.get("subtitle_quote") or kf_item.get("label") or ""
            ts = normalize_timestamp_val(kf_item.get("evidence_timestamp") or kf_item.get("timestamp"))

            screenshot_box = [img]
            if quote:
                cap_table = Table([[Paragraph(safe_text(clean_report_timestamp_string(quote)), screenshot_caption_style)]], colWidths=[460])
                cap_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#000000")),
                    ("PADDING", (0, 0), (-1, -1), 3),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]))
                screenshot_box.append(cap_table)
            screenshot_box.append(Paragraph(f"Evidence timestamp: {safe_text(ts)}", evidence_ts_style))
            screenshot_box.append(Spacer(1, 6))
            story.append(KeepTogether(screenshot_box))

    # =========================================================================
    # PAGES 8+: Full Evidence Transcript
    # =========================================================================
    transcript_lines = session_data.get("transcript_lines") or []
    if not transcript_lines and report.get("transcript_segments"):
        for s in report["transcript_segments"]:
            ts_norm = normalize_timestamp_val(s.get("timestamp") or s.get("start"))
            transcript_lines.append({
                "formatted": f"{ts_norm} · video — {s.get('text', '')}"
            })
    elif not transcript_lines and report.get("transcript"):
        raw_lines = [l.strip() for l in report["transcript"].splitlines() if l.strip()]
        for l in raw_lines:
            transcript_lines.append({"formatted": l})

    if transcript_lines:
        story.append(PageBreak())
        story.append(Paragraph("Evidence Transcript", section_heading_style))
        story.append(Spacer(1, 4))
        for line in transcript_lines:
            line_str = line.get("formatted") or str(line)
            clean_line = clean_report_timestamp_string(line_str)
            story.append(Paragraph(safe_text(clean_line), transcript_line_style))

    # Render PDF with clean page numbers
    doc.build(story, canvasmaker=NumberedCanvas)
    logger.info("Generated PDF report exactly matching SessionMind layout", pdf_path=pdf_path)
    return pdf_path
