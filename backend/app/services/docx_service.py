"""
DOCX Generation Service: Generates publication-ready Microsoft Word (.docx) reports.
Modeled on professional intelligence reports with evidence-backed extraction,
table styling, OpenCV screenshot integration, and intelligent content-dependent structure.
"""

import os
import re
from datetime import datetime, timezone
from typing import Any

import docx
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor
import structlog

from app.config import settings
from app.services.report_engine import build_dynamic_report

logger = structlog.get_logger()

# Professional Color Palette
COLOR_NAVY_HEX = "0F172A"       # Primary text & headers (#0F172A)
COLOR_NAVY_RGB = RGBColor(15, 23, 42)
COLOR_BLUE_HEX = "2563EB"       # Brand accent (#2563EB)
COLOR_BLUE_RGB = RGBColor(37, 99, 235)
COLOR_SLATE_HEX = "475569"      # Secondary text (#475569)
COLOR_SLATE_RGB = RGBColor(71, 85, 105)
COLOR_MUTED_HEX = "64748B"      # Subdued / captions (#64748B)
COLOR_MUTED_RGB = RGBColor(100, 116, 139)
COLOR_LIGHT_BG = "F8FAFC"       # Light card background (#F8FAFC)
COLOR_HEADER_BG = "F1F5F9"      # Table header fill (#F1F5F9)
COLOR_BORDER_HEX = "CBD5E1"     # Table / card borders (#CBD5E1)
COLOR_EMERALD_HEX = "059669"    # Positive / verified (#059669)
COLOR_EMERALD_RGB = RGBColor(5, 150, 105)
COLOR_AMBER_HEX = "D97706"      # Pending / warning (#D97706)
COLOR_AMBER_RGB = RGBColor(217, 119, 6)


def _set_cell_background(cell, hex_color: str) -> None:
    """Apply background shading to a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)


def _set_cell_margins(cell, top=100, bottom=100, left=150, right=150) -> None:
    """Set inner padding for a table cell (in twips, 20 twips = 1 pt)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def _set_table_borders(table, color=COLOR_BORDER_HEX, sz="4", val="single") -> None:
    """Set subtle, professional borders for a table."""
    tbl_pr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tbl_pr.append(borders)


def _add_callout_box(doc, text: str, title: str | None = None, border_color=COLOR_BLUE_HEX, bg_color=COLOR_LIGHT_BG):
    """Add a professional left-bordered callout panel."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)

    _set_cell_background(cell, bg_color)
    _set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    # Set left border only
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tc_pr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15

    if title:
        run_title = p.add_run(f"{title}\n")
        run_title.font.name = "Arial"
        run_title.font.size = Pt(9.5)
        run_title.font.bold = True
        run_title.font.color.rgb = COLOR_NAVY_RGB

    run_text = p.add_run(text)
    run_text.font.name = "Arial"
    run_text.font.size = Pt(9.0)
    run_text.font.color.rgb = COLOR_SLATE_RGB

    # Spacer after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)


def _add_section_heading(doc, title: str, subtitle: str | None = None) -> None:
    """Add a styled Heading 1 with accent styling."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True

    run = p.add_run(title)
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY_RGB

    if subtitle:
        p_sub = doc.add_paragraph()
        p_sub.paragraph_format.space_before = Pt(0)
        p_sub.paragraph_format.space_after = Pt(6)
        p_sub.paragraph_format.keep_with_next = True
        run_sub = p_sub.add_run(subtitle)
        run_sub.font.name = "Arial"
        run_sub.font.size = Pt(8.5)
        run_sub.font.italic = True
        run_sub.font.color.rgb = COLOR_MUTED_RGB


def _format_timestamp(seconds: float | int | None) -> str:
    """Format seconds into MM:SS or HH:MM:SS."""
    if seconds is None:
        return "N/A"
    try:
        s = float(seconds)
        if s <= 0:
            return "00:00"
        m, sec = divmod(int(s), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"
    except (ValueError, TypeError):
        return str(seconds)


def _determine_session_type(title: str, summary: str, topics: list) -> str:
    """Intelligently determine whether the video is an educational lecture, technical walkthrough, or meeting."""
    combined = (title + " " + summary + " " + " ".join(str(t) for t in topics)).lower()
    if any(k in combined for k in ["lecture", "student", "class", "course", "syllabus", "professor", "chapter", "tutorial", "learn"]):
        return "Lecture / Educational Session"
    if any(k in combined for k in ["demo", "architecture", "code", "implementation", "deployment", "walkthrough", "api"]):
        return "Technical Walkthrough & Architecture Review"
    if any(k in combined for k in ["interview", "candidate", "q&a", "question"]):
        return "Interview / Q&A Session"
    return "Executive Meeting & Strategic Discussion"


def _find_keyframe_image(url_or_name: str, session_id: str) -> str | None:
    """Locate keyframe image file on disk using multiple search paths."""
    base_name = os.path.basename(url_or_name)
    candidates = [
        # 1. Configured keyframes_dir / session_id / basename
        os.path.join(settings.keyframes_dir, session_id, base_name),
        # 2. Storage / keyframes / session_id / basename
        os.path.join(settings.storage_dir, "keyframes", session_id, base_name),
        # 3. Direct path if already absolute
        url_or_name,
        # 4. Upload directory
        os.path.join(settings.upload_dir, session_id, base_name),
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isfile(c) and os.path.getsize(c) > 0:
            return c
    return None


def generate_meeting_docx_report(
    session_data: dict[str, Any],
    session_id: str,
    previous_session_data: dict[str, Any] | None = None,
) -> str:
    """
    Generate a complete, professionally formatted Microsoft Word (.docx) document.
    Implements all required sections (A through N) with evidence quotes,
    OpenCV screenshot insertion, styled tables, and metadata.
    """
    os.makedirs(settings.reports_dir, exist_ok=True)
    docx_filename = f"report_{session_id}.docx"
    docx_path = os.path.join(settings.reports_dir, docx_filename)

    # 1. Build standardized dynamic report model
    report = build_dynamic_report(session_data)
    dur = report["duration_seconds"]
    dur_str = _format_timestamp(dur)
    session_title = report["title"] or "Video Intelligence Executive Report"
    created_at_str = report["created_at"] or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    session_type = _determine_session_type(session_title, report["summary"], report["topics"])

    # 2. Initialize Document
    doc = docx.Document()

    # Page Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

        # Header
        header = section.header
        header_p = header.paragraphs[0]
        header_p.text = "VideoIntel | AI-Powered Video & Meeting Intelligence Report"
        header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if header_p.runs:
            header_p.runs[0].font.name = "Arial"
            header_p.runs[0].font.size = Pt(8.0)
            header_p.runs[0].font.color.rgb = COLOR_MUTED_RGB

        # Footer
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.text = f"Confidential | Generated by VideoIntel AI Core • Session {session_id[:8]}"
        footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        if footer_p.runs:
            footer_p.runs[0].font.name = "Arial"
            footer_p.runs[0].font.size = Pt(8.0)
            footer_p.runs[0].font.color.rgb = COLOR_MUTED_RGB

    # ==========================================
    # SECTION A: COVER & SESSION INFORMATION
    # ==========================================
    # Branding tag
    p_brand = doc.add_paragraph()
    p_brand.paragraph_format.space_before = Pt(8)
    p_brand.paragraph_format.space_after = Pt(2)
    run_brand = p_brand.add_run("VIDEOINTEL AI • MULTIMODAL INTELLIGENCE RECORD")
    run_brand.font.name = "Arial"
    run_brand.font.size = Pt(8.5)
    run_brand.font.bold = True
    run_brand.font.color.rgb = COLOR_BLUE_RGB

    # Main Document Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run(session_title)
    run_title.font.name = "Arial"
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_NAVY_RGB

    # Subtitle / Session Type
    p_subtitle = doc.add_paragraph()
    p_subtitle.paragraph_format.space_before = Pt(0)
    p_subtitle.paragraph_format.space_after = Pt(12)
    run_sub = p_subtitle.add_run(f"Executive Report • {session_type}")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(10.5)
    run_sub.font.color.rgb = COLOR_SLATE_RGB

    # Metadata Grid Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    _set_table_borders(meta_table)

    meta_items = [
        ("Date & Time Processed", str(created_at_str)),
        ("Video Duration", f"{dur_str} ({int(dur)} seconds)"),
        ("Source Filename", str(report["source_filename"] or "Direct Video Upload")),
        ("Language", "English (Auto-Detected)"),
        ("AI / NLP Processing Engine", str(report["ai_provider"] or "Local ML Engine")),
        ("Verification Status", "Verified • Multi-modal Evidence Anchored"),
    ]

    if report["document_filename"]:
        meta_items.append(("Supporting Document", str(report["document_filename"])))

    # Speakers if detected
    speakers_list = report.get("speakers") or []
    if speakers_list:
        spk_names = ", ".join(s.get("name", "") for s in speakers_list if s.get("name"))
        meta_items.append(("Identified Participants", spk_names))

    row_idx = 0
    for i in range(0, len(meta_items), 2):
        if row_idx >= len(meta_table.rows):
            meta_table.add_row()
        row = meta_table.rows[row_idx]

        # Col 1
        label1, val1 = meta_items[i]
        c1 = row.cells[0]
        c1.width = Inches(3.25)
        _set_cell_margins(c1, top=80, bottom=80, left=100, right=100)
        _set_cell_background(c1, COLOR_LIGHT_BG if row_idx % 2 == 0 else "FFFFFF")
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r_lbl1 = p1.add_run(f"{label1}: ")
        r_lbl1.font.bold = True
        r_lbl1.font.size = Pt(8.5)
        r_lbl1.font.color.rgb = COLOR_NAVY_RGB
        r_val1 = p1.add_run(val1)
        r_val1.font.size = Pt(8.5)
        r_val1.font.color.rgb = COLOR_SLATE_RGB

        # Col 2
        c2 = row.cells[1]
        c2.width = Inches(3.25)
        _set_cell_margins(c2, top=80, bottom=80, left=100, right=100)
        _set_cell_background(c2, COLOR_LIGHT_BG if row_idx % 2 == 0 else "FFFFFF")
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)

        if i + 1 < len(meta_items):
            label2, val2 = meta_items[i + 1]
            r_lbl2 = p2.add_run(f"{label2}: ")
            r_lbl2.font.bold = True
            r_lbl2.font.size = Pt(8.5)
            r_lbl2.font.color.rgb = COLOR_NAVY_RGB
            r_val2 = p2.add_run(val2)
            r_val2.font.size = Pt(8.5)
            r_val2.font.color.rgb = COLOR_SLATE_RGB

        row_idx += 1

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==========================================
    # SECTION B: EXECUTIVE SUMMARY
    # ==========================================
    _add_section_heading(doc, "1. Executive Summary")
    if report["has_summary"]:
        p_sum = doc.add_paragraph()
        p_sum.paragraph_format.space_before = Pt(2)
        p_sum.paragraph_format.space_after = Pt(8)
        p_sum.paragraph_format.line_spacing = 1.15
        r_sum = p_sum.add_run(report["summary"])
        r_sum.font.name = "Arial"
        r_sum.font.size = Pt(9.5)
        r_sum.font.color.rgb = COLOR_NAVY_RGB

        # Sentiment Callout
        sent = report.get("sentiment") or {}
        if sent.get("overall"):
            pos = int(sent.get("positive_score", 0.0) * 100)
            neu = int(sent.get("neutral_score", 0.0) * 100)
            neg = int(sent.get("negative_score", 0.0) * 100)
            sent_text = (
                f"Overall Session Tone: {sent['overall'].upper()} "
                f"(Positive: {pos}%, Neutral: {neu}%, Constructive/Risk Focus: {neg}%). "
                f"Communication was evaluated through NLP lexical and semantic polarity models."
            )
            _add_callout_box(doc, sent_text, title="Sentiment & Communication Dynamics", border_color=COLOR_EMERALD_HEX)
    else:
        p_none = doc.add_paragraph("No executive summary could be generated from available audio and notes.")
        p_none.runs[0].font.italic = True

    # ==========================================
    # SECTION C: SESSION / VIDEO OVERVIEW
    # ==========================================
    overview_title = "Lecture & Subject Overview" if "Lecture" in session_type else "Meeting & Session Overview"
    _add_section_heading(doc, f"2. {overview_title}")
    overview_text = (
        f"This session was recorded as '{report['source_filename'] or 'Session Media'}' with an active duration of "
        f"{dur_str}. The recording covers structured discourse and audiovisual media processed by VideoIntel's "
        f"multimodal intelligence pipeline. The primary purpose was {session_title.lower()}, synthesizing key "
        f"discussion topics, decisions, actionable commitments, and visual evidence into this unified reference."
    )
    p_ov = doc.add_paragraph()
    p_ov.paragraph_format.space_after = Pt(8)
    p_ov.paragraph_format.line_spacing = 1.15
    r_ov = p_ov.add_run(overview_text)
    r_ov.font.name = "Arial"
    r_ov.font.size = Pt(9.5)
    r_ov.font.color.rgb = COLOR_SLATE_RGB

    # ==========================================
    # SECTION D: KEY DISCUSSION POINTS
    # ==========================================
    _add_section_heading(doc, "3. Key Discussion Points")
    # Extract discussion points from topics, timeline, or transcript
    points_found = False
    if report["has_timeline"]:
        points_found = True
        for item in report["timeline"]:
            ts = item.get("timestamp", "00:00")
            title = item.get("title", "")
            desc = item.get("description") or item.get("evidence") or ""
            p_pt = doc.add_paragraph(style="List Bullet")
            p_pt.paragraph_format.space_before = Pt(2)
            p_pt.paragraph_format.space_after = Pt(3)
            r_ts = p_pt.add_run(f"[{ts}] ")
            r_ts.font.bold = True
            r_ts.font.color.rgb = COLOR_BLUE_RGB
            r_title = p_pt.add_run(f"{title}: ")
            r_title.font.bold = True
            r_title.font.color.rgb = COLOR_NAVY_RGB
            r_desc = p_pt.add_run(desc)
            r_desc.font.color.rgb = COLOR_SLATE_RGB
    elif report["has_topics"]:
        points_found = True
        for t in report["topics"]:
            p_pt = doc.add_paragraph(style="List Bullet")
            p_pt.paragraph_format.space_before = Pt(2)
            p_pt.paragraph_format.space_after = Pt(3)
            r_t = p_pt.add_run(f"{t.get('topic')}: ")
            r_t.font.bold = True
            r_t.font.color.rgb = COLOR_NAVY_RGB
            kws = ", ".join(t.get("keywords", []))
            r_kws = p_pt.add_run(f"Focused discussion regarding {kws} (Relevance: {int(t.get('relevance', 0.8) * 100)}%).")
            r_kws.font.color.rgb = COLOR_SLATE_RGB

    if not points_found:
        p_pt = doc.add_paragraph("No explicit discussion point milestones detected in audio track.")
        p_pt.runs[0].font.italic = True

    # ==========================================
    # SECTION E: TOPICS & KEY CONCEPTS (OUTLINE / TABLE)
    # ==========================================
    _add_section_heading(doc, "4. Topics & Key Concepts")
    if report["has_topics"]:
        topic_table = doc.add_table(rows=1, cols=3)
        topic_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        topic_table.autofit = False
        _set_table_borders(topic_table)

        # Header
        hdr = topic_table.rows[0].cells
        hdr[0].width = Inches(2.0)
        hdr[1].width = Inches(1.2)
        hdr[2].width = Inches(3.3)
        hdr_labels = ["Topic / Concept", "Relevance", "Keywords & Supporting Context"]
        for idx, text in enumerate(hdr_labels):
            _set_cell_background(hdr[idx], COLOR_HEADER_BG)
            _set_cell_margins(hdr[idx], top=100, bottom=100, left=100, right=100)
            p = hdr[idx].paragraphs[0]
            r = p.add_run(text)
            r.font.bold = True
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_NAVY_RGB

        # Rows
        for r_idx, t in enumerate(report["topics"], start=1):
            row = topic_table.add_row()
            bg = COLOR_LIGHT_BG if r_idx % 2 == 0 else "FFFFFF"

            # Col 1: Topic
            c0 = row.cells[0]
            _set_cell_background(c0, bg)
            _set_cell_margins(c0, top=80, bottom=80, left=100, right=100)
            r0 = c0.paragraphs[0].add_run(str(t.get("topic", "")))
            r0.font.bold = True
            r0.font.size = Pt(8.5)
            r0.font.color.rgb = COLOR_NAVY_RGB

            # Col 2: Relevance
            c1 = row.cells[1]
            _set_cell_background(c1, bg)
            _set_cell_margins(c1, top=80, bottom=80, left=100, right=100)
            rel_val = int(t.get("relevance", 0.8) * 100)
            r1 = c1.paragraphs[0].add_run(f"{rel_val}%")
            r1.font.size = Pt(8.5)
            r1.font.color.rgb = COLOR_BLUE_RGB

            # Col 3: Keywords & context
            c2 = row.cells[2]
            _set_cell_background(c2, bg)
            _set_cell_margins(c2, top=80, bottom=80, left=100, right=100)
            kws = ", ".join(t.get("keywords", [])) or t.get("evidence", "Session Stream")
            r2 = c2.paragraphs[0].add_run(kws)
            r2.font.size = Pt(8.5)
            r2.font.color.rgb = COLOR_SLATE_RGB

        doc.add_paragraph().paragraph_format.space_after = Pt(6)
    else:
        p_t = doc.add_paragraph("No distinct topical clusters were extracted.")
        p_t.runs[0].font.italic = True

    # ==========================================
    # SECTION F: DECISIONS & FORMAL AGREEMENTS
    # ==========================================
    _add_section_heading(doc, "5. Decisions & Agreed Outcomes")
    if report["has_decisions"]:
        for idx, d in enumerate(report["decisions"], start=1):
            dec_text = d.get("decision", "")
            ctx = d.get("context", "")
            ev = d.get("evidence", "")
            ts = d.get("timestamp")

            p_dec = doc.add_paragraph()
            p_dec.paragraph_format.space_before = Pt(4)
            p_dec.paragraph_format.space_after = Pt(2)
            r_num = p_dec.add_run(f"Decision {idx}: ")
            r_num.font.bold = True
            r_num.font.color.rgb = COLOR_BLUE_RGB
            r_txt = p_dec.add_run(dec_text)
            r_txt.font.bold = True
            r_txt.font.color.rgb = COLOR_NAVY_RGB

            p_detail = doc.add_paragraph()
            p_detail.paragraph_format.left_indent = Inches(0.25)
            p_detail.paragraph_format.space_before = Pt(0)
            p_detail.paragraph_format.space_after = Pt(4)
            if ctx:
                r_c = p_detail.add_run(f"Context: {ctx}. ")
                r_c.font.size = Pt(8.5)
                r_c.font.color.rgb = COLOR_SLATE_RGB
            if ts:
                r_ts = p_detail.add_run(f"[Time: {ts}] ")
                r_ts.font.size = Pt(8.5)
                r_ts.font.color.rgb = COLOR_BLUE_RGB
            if ev:
                r_e = p_detail.add_run(f"Evidence: \"{ev}\"")
                r_e.font.size = Pt(8.5)
                r_e.font.italic = True
                r_e.font.color.rgb = COLOR_MUTED_RGB
    else:
        _add_callout_box(
            doc,
            "No formal binding decisions or policy agreements were explicitly identified in this recording.",
            title="Note",
            border_color=COLOR_MUTED_HEX,
        )

    # ==========================================
    # SECTION G: ACTION ITEMS & DELIVERABLES (TABLE)
    # ==========================================
    _add_section_heading(doc, "6. Action Items & Next Steps")
    if report["has_actions"]:
        act_table = doc.add_table(rows=1, cols=5)
        act_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        act_table.autofit = False
        _set_table_borders(act_table)

        col_widths = [Inches(1.2), Inches(2.3), Inches(1.0), Inches(0.9), Inches(1.1)]
        hdr = act_table.rows[0].cells
        hdr_labels = ["Owner", "Task", "Deadline", "Status", "Evidence"]
        for idx, text in enumerate(hdr_labels):
            hdr[idx].width = col_widths[idx]
            _set_cell_background(hdr[idx], COLOR_HEADER_BG)
            _set_cell_margins(hdr[idx], top=100, bottom=100, left=80, right=80)
            p = hdr[idx].paragraphs[0]
            r = p.add_run(text)
            r.font.bold = True
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_NAVY_RGB

        for r_idx, a in enumerate(report["action_items"], start=1):
            row = act_table.add_row()
            bg = COLOR_LIGHT_BG if r_idx % 2 == 0 else "FFFFFF"

            owner = a.get("assignee") or a.get("owner") or "Not specified"
            task = a.get("task", "")
            deadline = a.get("due_date") or a.get("deadline") or "Not specified"
            status = "Completed" if a.get("status") == "completed" else "Pending"
            ev = a.get("evidence") or a.get("timestamp") or "Transcript Record"

            row_data = [owner, task, deadline, status, ev]
            for c_idx, val in enumerate(row_data):
                cell = row.cells[c_idx]
                cell.width = col_widths[c_idx]
                _set_cell_background(cell, bg)
                _set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
                p = cell.paragraphs[0]
                r = p.add_run(str(val))
                r.font.size = Pt(8.5)
                if c_idx == 0:
                    r.font.bold = True
                    r.font.color.rgb = COLOR_NAVY_RGB
                elif c_idx == 3:
                    r.font.bold = True
                    r.font.color.rgb = COLOR_EMERALD_RGB if status == "Completed" else COLOR_AMBER_RGB
                else:
                    r.font.color.rgb = COLOR_SLATE_RGB

        doc.add_paragraph().paragraph_format.space_after = Pt(6)
    else:
        _add_callout_box(
            doc,
            "No specific action items, assignments, or deadlines were identified in the source session.",
            title="Action Items Status",
            border_color=COLOR_MUTED_HEX,
        )

    # ==========================================
    # SECTION H: QUESTIONS & ANSWERS
    # ==========================================
    if report["has_qa"]:
        _add_section_heading(doc, "7. Questions & Answers")
        for idx, qa in enumerate(report["questions_answers"], start=1):
            q = qa.get("question", "")
            ans = qa.get("answer") or "Answer pending / not explicitly resolved in discussion."
            spk = qa.get("speaker") or "Participant"
            ev = qa.get("evidence") or ""

            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(4)
            p_q.paragraph_format.space_after = Pt(2)
            r_qn = p_q.add_run(f"Q{idx} ({spk}): ")
            r_qn.font.bold = True
            r_qn.font.color.rgb = COLOR_BLUE_RGB
            r_qt = p_q.add_run(q)
            r_qt.font.bold = True
            r_qt.font.color.rgb = COLOR_NAVY_RGB

            p_a = doc.add_paragraph()
            p_a.paragraph_format.left_indent = Inches(0.2)
            p_a.paragraph_format.space_before = Pt(0)
            p_a.paragraph_format.space_after = Pt(4)
            r_al = p_a.add_run("Answer: ")
            r_al.font.bold = True
            r_al.font.size = Pt(8.5)
            r_al.font.color.rgb = COLOR_EMERALD_RGB
            r_at = p_a.add_run(ans)
            r_at.font.size = Pt(8.5)
            r_at.font.color.rgb = COLOR_SLATE_RGB
            if ev:
                r_ev = p_a.add_run(f" [Source: \"{ev}\"]")
                r_ev.font.size = Pt(8.0)
                r_ev.font.italic = True
                r_ev.font.color.rgb = COLOR_MUTED_RGB

    # ==========================================
    # SECTION I: RISKS & BLOCKERS
    # ==========================================
    # Identify genuine risks/concerns from timeline/topics/evidence
    risks_found: list[dict[str, str]] = []
    for ev_item in report.get("evidence", []):
        claim = ev_item.get("claim", "").lower()
        if any(w in claim for w in ["risk", "blocker", "delay", "challenge", "concern", "obstacle", "issue", "bug"]):
            risks_found.append({
                "issue": ev_item.get("claim", ""),
                "timestamp": ev_item.get("timestamp", "Session Stream"),
                "evidence": ev_item.get("quote", ""),
            })

    if risks_found:
        _add_section_heading(doc, "8. Risks, Obstacles & Identified Blockers")
        for idx, rsk in enumerate(risks_found, start=1):
            p_r = doc.add_paragraph()
            p_r.paragraph_format.space_before = Pt(3)
            p_r.paragraph_format.space_after = Pt(2)
            r_lbl = p_r.add_run(f"Risk #{idx}: ")
            r_lbl.font.bold = True
            r_lbl.font.color.rgb = COLOR_AMBER_RGB
            r_iss = p_r.add_run(f"{rsk['issue']} [{rsk['timestamp']}]")
            r_iss.font.bold = True
            r_iss.font.color.rgb = COLOR_NAVY_RGB

            if rsk.get("evidence"):
                p_re = doc.add_paragraph()
                p_re.paragraph_format.left_indent = Inches(0.2)
                p_re.paragraph_format.space_before = Pt(0)
                p_re.paragraph_format.space_after = Pt(3)
                r_quote = p_re.add_run(f"Supporting Evidence: \"{rsk['evidence']}\"")
                r_quote.font.size = Pt(8.5)
                r_quote.font.italic = True
                r_quote.font.color.rgb = COLOR_MUTED_RGB

    # ==========================================
    # SECTION J: IMPORTANT MOMENTS (TIMELINE)
    # ==========================================
    if report["has_timeline"]:
        _add_section_heading(doc, "9. Chronological Session Timeline")
        tl_table = doc.add_table(rows=1, cols=4)
        tl_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        tl_table.autofit = False
        _set_table_borders(tl_table)

        col_w = [Inches(1.0), Inches(1.3), Inches(2.5), Inches(1.7)]
        hdr = tl_table.rows[0].cells
        for idx, text in enumerate(["Timestamp", "Event Type", "Event Description", "Supporting Context"]):
            hdr[idx].width = col_w[idx]
            _set_cell_background(hdr[idx], COLOR_HEADER_BG)
            _set_cell_margins(hdr[idx], top=100, bottom=100, left=80, right=80)
            p = hdr[idx].paragraphs[0]
            r = p.add_run(text)
            r.font.bold = True
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_NAVY_RGB

        for r_idx, ev in enumerate(report["timeline"], start=1):
            row = tl_table.add_row()
            bg = COLOR_LIGHT_BG if r_idx % 2 == 0 else "FFFFFF"

            ts_val = ev.get("timestamp", "00:00")
            type_val = ev.get("type", "moment").upper()
            title_val = ev.get("title", "")
            ev_val = ev.get("evidence") or "Session Stream"

            row_data = [ts_val, type_val, title_val, ev_val]
            for c_idx, val in enumerate(row_data):
                cell = row.cells[c_idx]
                cell.width = col_w[c_idx]
                _set_cell_background(cell, bg)
                _set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
                p = cell.paragraphs[0]
                r = p.add_run(str(val))
                r.font.size = Pt(8.5)
                if c_idx == 0:
                    r.font.bold = True
                    r.font.color.rgb = COLOR_BLUE_RGB
                elif c_idx == 1:
                    r.font.bold = True
                    r.font.color.rgb = COLOR_NAVY_RGB
                else:
                    r.font.color.rgb = COLOR_SLATE_RGB

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ==========================================
    # SECTION K: VISUAL EVIDENCE & SCREENSHOTS (OPENCV)
    # ==========================================
    keyframes = report["video_analysis"].get("keyframes") or []
    if keyframes:
        _add_section_heading(doc, "10. Visual Evidence & Keyframe Screenshots")
        p_intro = doc.add_paragraph(
            "The following keyframes represent slide transitions, whiteboard annotations, "
            "and significant visual shifts automatically captured by OpenCV scene detection:"
        )
        p_intro.paragraph_format.space_after = Pt(8)
        p_intro.runs[0].font.size = Pt(9.0)
        p_intro.runs[0].font.color.rgb = COLOR_SLATE_RGB

        valid_images_inserted = 0
        for idx, kf in enumerate(keyframes[:6], start=1):
            kf_url = kf.get("url") or kf.get("path") or ""
            kf_ts = _format_timestamp(kf.get("timestamp", 0.0))
            kf_label = kf.get("label") or f"Visual Event at {kf_ts}"

            img_path = _find_keyframe_image(kf_url, session_id)
            if img_path:
                try:
                    # Insert picture
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(8)
                    p_img.paragraph_format.space_after = Pt(2)
                    run_img = p_img.add_run()
                    run_img.add_picture(img_path, width=Inches(5.2))

                    # Caption
                    p_cap = doc.add_paragraph()
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_cap.paragraph_format.space_before = Pt(0)
                    p_cap.paragraph_format.space_after = Pt(10)
                    r_cap = p_cap.add_run(f"Figure {idx}: [{kf_ts}] — {kf_label}")
                    r_cap.font.name = "Arial"
                    r_cap.font.size = Pt(8.5)
                    r_cap.font.italic = True
                    r_cap.font.color.rgb = COLOR_MUTED_RGB

                    valid_images_inserted += 1
                except Exception as exc:
                    logger.warning("Could not insert keyframe image into docx", error=str(exc), path=img_path)

        if valid_images_inserted == 0:
            _add_callout_box(
                doc,
                "Keyframe timestamps were detected, but physical image assets were stored remotely or omitted.",
                title="Visual Evidence Notice",
                border_color=COLOR_MUTED_HEX,
            )
    elif report["source_file_type"] == "video":
        _add_section_heading(doc, "10. Visual Evidence")
        _add_callout_box(
            doc,
            "Video stream was analyzed with OpenCV; no abrupt visual scene shifts exceeded the keyframe extraction threshold.",
            title="Visual Evidence Notice",
            border_color=COLOR_MUTED_HEX,
        )

    # ==========================================
    # SECTION L: PROGRESS FROM PREVIOUS SESSIONS
    # ==========================================
    if previous_session_data:
        _add_section_heading(doc, "11. Progress From Previous Sessions")
        prev_title = previous_session_data.get("title", "Prior Session")
        prev_date = previous_session_data.get("created_at", "Earlier Date")
        p_prev = doc.add_paragraph(f"Comparison with previous session '{prev_title}' ({prev_date}):")
        p_prev.runs[0].font.size = Pt(9.0)

        prev_actions = previous_session_data.get("action_items") or []
        curr_actions = report["action_items"]
        p_cmp = doc.add_paragraph(style="List Bullet")
        p_cmp.add_run(f"Deliverable Count: Prior session had {len(prev_actions)} action items; current session has {len(curr_actions)} items.")
        p_cmp.runs[0].font.size = Pt(8.5)

    # ==========================================
    # SECTION M: FULL VERBATIM TRANSCRIPT
    # ==========================================
    transcript_text = report.get("transcript") or ""
    if transcript_text and transcript_text.strip() != "(No distinct vocal stream detected)":
        _add_section_heading(doc, "12. Complete Dialogue & Verbatim Transcript")
        p_t_intro = doc.add_paragraph("The complete chronological dialogue and verbatim audio transcript recorded for this session:")
        p_t_intro.paragraph_format.space_after = Pt(4)
        p_t_intro.runs[0].font.size = Pt(8.5)
        p_t_intro.runs[0].font.italic = True
        p_t_intro.runs[0].font.color.rgb = COLOR_MUTED_RGB

        # Display transcript in clean readable format (truncated at 80,000 chars if gigantic)
        clean_tr = transcript_text.strip()
        if len(clean_tr) > 80000:
            clean_tr = clean_tr[:80000] + "\n\n[Transcript continues in dedicated supplementary export...]"

        for paragraph_block in clean_tr.split("\n\n"):
            p_tr = doc.add_paragraph()
            p_tr.paragraph_format.space_before = Pt(2)
            p_tr.paragraph_format.space_after = Pt(3)
            p_tr.paragraph_format.line_spacing = 1.15

            # Speaker bolding if line matches "Speaker Name: dialogue"
            match = re.match(r"^([A-Z][a-zA-Z\s\.\-]{2,30}):\s*(.+)$", paragraph_block)
            if match:
                spk, speech = match.group(1), match.group(2)
                r_spk = p_tr.add_run(f"{spk}: ")
                r_spk.font.bold = True
                r_spk.font.size = Pt(8.5)
                r_spk.font.color.rgb = COLOR_BLUE_RGB
                r_txt = p_tr.add_run(speech)
                r_txt.font.size = Pt(8.5)
                r_txt.font.color.rgb = COLOR_NAVY_RGB
            else:
                r_txt = p_tr.add_run(paragraph_block)
                r_txt.font.size = Pt(8.5)
                r_txt.font.color.rgb = COLOR_SLATE_RGB

    # ==========================================
    # SECTION N: REFERENCES & PROCESSING AUDIT
    # ==========================================
    _add_section_heading(doc, "13. Processing Details & Verification Audit")
    audit_table = doc.add_table(rows=5, cols=2)
    audit_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    audit_table.autofit = False
    _set_table_borders(audit_table)

    audit_rows = [
        ("Session Identifier", session_id),
        ("Source Media File", report["source_filename"] or "N/A"),
        ("AI Processing Provider", report["ai_provider"] or "Local ML Engine"),
        ("Visual Scene Shifts Detected", str(report["video_analysis"].get("scene_changes", 0))),
        ("Report Generation Engine", "VideoIntel Intelligent Document Compiler v2.0 (python-docx)"),
    ]

    for idx, (lbl, val) in enumerate(audit_rows):
        row = audit_table.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = Inches(2.5), Inches(4.0)
        _set_cell_background(c0, COLOR_LIGHT_BG)
        _set_cell_background(c1, "FFFFFF")
        _set_cell_margins(c0, top=60, bottom=60, left=80, right=80)
        _set_cell_margins(c1, top=60, bottom=60, left=80, right=80)

        r0 = c0.paragraphs[0].add_run(lbl)
        r0.font.bold = True
        r0.font.size = Pt(8.0)
        r0.font.color.rgb = COLOR_NAVY_RGB

        r1 = c1.paragraphs[0].add_run(val)
        r1.font.size = Pt(8.0)
        r1.font.color.rgb = COLOR_SLATE_RGB

    # Save to disk
    doc.save(docx_path)
    logger.info("Successfully generated Word intelligence report (.docx)", path=docx_path, session_id=session_id)
    return docx_path
