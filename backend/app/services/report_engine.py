"""
Dynamic Report Engine: Builds consistent, evidence-backed reports from actual meeting intelligence data.
Ensures identical reporting across Frontend, PDF, Markdown/TXT, and JSON exports.
Sections are ONLY included if supported by actual data.
"""

from typing import Any
import re


def build_dynamic_report(session_data: dict[str, Any]) -> dict[str, Any]:
    """
    Constructs a dynamic report structure from real session data.
    Evaluates what data is actually present and returns only active sections.
    """
    summary = (session_data.get("summary") or "").strip()
    topics = session_data.get("topics") or []
    action_items = session_data.get("action_items") or []
    decisions = session_data.get("decisions") or []
    questions_answers = session_data.get("questions_answers") or []
    timeline = session_data.get("timeline") or []
    speakers = session_data.get("speakers") or []
    video_analysis = session_data.get("video_analysis") or {}
    document_analysis = session_data.get("document_analysis") or {}
    evidence = session_data.get("evidence") or []
    transcript = (session_data.get("transcript") or "").strip()

    keyframes = video_analysis.get("keyframes") or []
    scene_changes = video_analysis.get("scene_changes", 0)
    has_video_evidence = bool(keyframes or scene_changes > 0 or session_data.get("source_file_type") == "video")

    doc_pages = document_analysis.get("pages") or []
    has_document_evidence = bool(doc_pages or session_data.get("document_filename"))

    meeting_overview = (session_data.get("meeting_overview") or "").strip()
    key_discussion_points = session_data.get("key_discussion_points") or []
    open_questions = session_data.get("open_questions") or []
    risks_blockers = session_data.get("risks_blockers") or []
    important_moments = session_data.get("important_moments") or []
    changes_from_previous = session_data.get("changes_from_previous") or "None recorded."
    topics_mind_map = session_data.get("topics_mind_map") or []
    transcript_segments = session_data.get("transcript_segments") or []

    # Normalized decisions (support both string and dict)
    normalized_decisions = []
    for d in decisions:
        if isinstance(d, dict):
            normalized_decisions.append(d)
        elif isinstance(d, str):
            clean_str = re.sub(r"^Agreed:\s*", "", d).strip()
            normalized_decisions.append({
                "decision": clean_str,
                "context": "Agreement reached during session discussion",
                "participants": "Meeting Participants",
                "timestamp": None,
                "evidence": d,
            })

    # Normalized action items (ensure status and evidence fields)
    normalized_actions = []
    for a in action_items:
        if isinstance(a, dict):
            item = dict(a)
            if "status" not in item:
                item["status"] = "pending"
            normalized_actions.append(item)

    # Active section determination
    active_sections: list[str] = ["executive_summary"] if summary else []
    if meeting_overview:
        active_sections.append("meeting_overview")
    if topics:
        active_sections.append("topics")
    if key_discussion_points:
        active_sections.append("key_discussion_points")
    if normalized_actions:
        active_sections.append("action_items")
    if normalized_decisions:
        active_sections.append("decisions")
    if open_questions:
        active_sections.append("open_questions")
    if risks_blockers:
        active_sections.append("risks_blockers")
    if important_moments:
        active_sections.append("important_moments")
    if topics_mind_map:
        active_sections.append("topics_mind_map")
    if questions_answers:
        active_sections.append("questions_answers")
    if timeline:
        active_sections.append("timeline")
    if has_video_evidence:
        active_sections.append("visual_intelligence")
    if has_document_evidence:
        active_sections.append("document_analysis")
    if speakers:
        active_sections.append("speakers")
    if evidence:
        active_sections.append("evidence")
    if transcript or transcript_segments:
        active_sections.append("transcript")

    return {
        "title": session_data.get("title") or "Executive Meeting Intelligence Report",
        "session_id": session_data.get("id"),
        "created_at": session_data.get("created_at"),
        "duration_seconds": session_data.get("duration_seconds", 0.0),
        "source_filename": session_data.get("source_filename"),
        "source_file_type": session_data.get("source_file_type"),
        "document_filename": session_data.get("document_filename"),
        "ai_provider": session_data.get("ai_provider", "Local ML Engine"),
        "active_sections": active_sections,
        "has_summary": bool(summary),
        "summary": summary,
        "has_overview": bool(meeting_overview),
        "meeting_overview": meeting_overview,
        "has_key_points": bool(key_discussion_points),
        "key_discussion_points": key_discussion_points,
        "has_topics": bool(topics),
        "topics": topics,
        "has_actions": bool(normalized_actions),
        "action_items": normalized_actions,
        "has_decisions": bool(normalized_decisions),
        "decisions": normalized_decisions,
        "has_open_questions": bool(open_questions),
        "open_questions": open_questions,
        "has_risks_blockers": bool(risks_blockers),
        "risks_blockers": risks_blockers,
        "has_important_moments": bool(important_moments),
        "important_moments": important_moments,
        "changes_from_previous": changes_from_previous,
        "has_mind_map": bool(topics_mind_map),
        "topics_mind_map": topics_mind_map,
        "has_qa": bool(questions_answers),
        "questions_answers": questions_answers,
        "has_timeline": bool(timeline),
        "timeline": timeline,
        "has_visual": has_video_evidence,
        "video_analysis": video_analysis,
        "has_document": has_document_evidence,
        "document_analysis": document_analysis,
        "has_speakers": bool(speakers),
        "speakers": speakers,
        "has_evidence": bool(evidence),
        "evidence": evidence,
        "sentiment": session_data.get("sentiment") or {},
        "transcript": transcript,
        "transcript_segments": transcript_segments,
    }


def generate_json_export(session_data: dict[str, Any]) -> dict[str, Any]:
    """
    Produce a clean, structured JSON export matching project schema.
    """
    report = build_dynamic_report(session_data)
    return {
        "session": {
            "id": report["session_id"],
            "title": report["title"],
            "created_at": report["created_at"],
            "duration_seconds": report["duration_seconds"],
            "source_filename": report["source_filename"],
            "source_file_type": report["source_file_type"],
            "document_filename": report["document_filename"],
            "ai_provider": report["ai_provider"],
            "active_sections": report["active_sections"],
        },
        "summary": {
            "text": report["summary"],
            "sentiment": report["sentiment"],
        },
        "topics": report["topics"],
        "action_items": report["action_items"],
        "decisions": report["decisions"],
        "questions_answers": report["questions_answers"],
        "timeline": report["timeline"],
        "speakers": report["speakers"],
        "visual_evidence": {
            "keyframes": report["video_analysis"].get("keyframes", []),
            "scene_changes": report["video_analysis"].get("scene_changes", 0),
            "visual_activity": report["video_analysis"].get("visual_activity", 0.0),
        },
        "documents": report["document_analysis"],
        "evidence": report["evidence"],
        "transcript": report["transcript"],
    }


def generate_markdown_report(session_data: dict[str, Any]) -> str:
    """
    Produce a clean, dynamic GitHub-flavored Markdown / Text report.
    Only includes sections that contain actual data.
    """
    report = build_dynamic_report(session_data)
    dur = report["duration_seconds"]
    dur_str = f"{int(dur // 60)}m {int(dur % 60)}s" if dur > 0 else "N/A"

    lines: list[str] = [
        f"# {report['title']}",
        f"**Generated by MeetingMind AI Core** | AI Engine: `{report['ai_provider']}`",
        "",
        "---",
        "",
        "## Session Metadata",
        f"- **Session ID:** `{report['session_id']}`",
        f"- **Date & Time:** {report['created_at'] or 'N/A'}",
        f"- **Duration:** {dur_str}",
        f"- **Source Media:** {report['source_filename'] or 'N/A'} ({report['source_file_type'] or 'unknown'})",
    ]

    if report["document_filename"]:
        lines.append(f"- **Supporting Document:** {report['document_filename']}")

    lines.append("")

    # 1. Executive Summary
    if report["has_summary"]:
        lines.extend([
            "---",
            "",
            "## 1. Executive Summary",
            report["summary"],
            "",
        ])
        if report["sentiment"].get("overall"):
            lines.append(f"**Discussion Sentiment:** {report['sentiment']['overall']} "
                         f"(Positive: {int(report['sentiment'].get('positive_score', 0) * 100)}%, "
                         f"Neutral: {int(report['sentiment'].get('neutral_score', 0) * 100)}%, "
                         f"Constructive: {int(report['sentiment'].get('negative_score', 0) * 100)}%)")
            lines.append("")

    # 2. Key Topics
    if report["has_topics"]:
        lines.extend([
            "---",
            "",
            "## 2. Key Discussion Topics",
            "| Topic | Relevance | Supporting Evidence / Keywords |",
            "| :--- | :--- | :--- |",
        ])
        for t in report["topics"]:
            rel = f"{int(t.get('relevance', 0.8) * 100)}%"
            kws = ", ".join(t.get("keywords", [])) or t.get("evidence", "Session Discussion")
            lines.append(f"| **{t.get('topic')}** | {rel} | {kws} |")
        lines.append("")

    # 3. Action Items
    if report["has_actions"]:
        lines.extend([
            "---",
            "",
            "## 3. Action Items & Deliverables",
            "| Task | Assignee | Priority | Deadline | Status | Evidence |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ])
        for a in report["action_items"]:
            task = a.get("task", "")
            assignee = a.get("assignee", "Unassigned")
            priority = a.get("priority", "Medium")
            due = a.get("due_date") or "Not specified"
            status = "Completed" if a.get("status") == "completed" else "Pending"
            ev = a.get("evidence") or a.get("timestamp") or "Transcript Record"
            lines.append(f"| {task} | {assignee} | {priority} | {due} | {status} | `{ev}` |")
        lines.append("")

    # 4. Decisions
    if report["has_decisions"]:
        lines.extend([
            "---",
            "",
            "## 4. Formal Decisions & Agreements",
        ])
        for idx, d in enumerate(report["decisions"], start=1):
            dec_text = d.get("decision", "")
            ctx = d.get("context", "")
            participants = d.get("participants", "")
            ev = d.get("evidence", "")
            lines.append(f"### Decision #{idx}: {dec_text}")
            if ctx:
                lines.append(f"- **Context:** {ctx}")
            if participants:
                lines.append(f"- **Participants:** {participants}")
            if ev:
                lines.append(f"- **Evidence:** *\"{ev}\"*")
            lines.append("")

    # 5. Questions & Answers
    if report["has_qa"]:
        lines.extend([
            "---",
            "",
            "## 5. Questions & Answers",
        ])
        for idx, qa in enumerate(report["questions_answers"], start=1):
            q = qa.get("question", "")
            ans = qa.get("answer", "")
            spk = qa.get("speaker") or "Participant"
            ev = qa.get("evidence") or ""
            lines.append(f"**Q{idx} ({spk}):** {q}")
            lines.append(f"**Answer:** {ans}")
            if ev:
                lines.append(f"*Evidence Quote:* \"{ev}\"")
            lines.append("")

    # 6. Timeline
    if report["has_timeline"]:
        lines.extend([
            "---",
            "",
            "## 6. Chronological Session Timeline",
            "| Timestamp | Event Type | Details | Evidence |",
            "| :--- | :--- | :--- | :--- |",
        ])
        for ev in report["timeline"]:
            ts = ev.get("timestamp", "00:00")
            ev_type = ev.get("type", "moment").upper()
            title = ev.get("title", "")
            evidence_str = ev.get("evidence") or "Session Stream"
            lines.append(f"| `{ts}` | **{ev_type}** | {title} | {evidence_str} |")
        lines.append("")

    # 7. Visual Intelligence
    if report["has_visual"]:
        va = report["video_analysis"]
        lines.extend([
            "---",
            "",
            "## 7. OpenCV Visual Intelligence",
            f"- **Scene Shifts Detected:** {va.get('scene_changes', 0)}",
            f"- **Visual Activity Index:** {va.get('visual_activity', 0.0)}%",
            f"- **Keyframes Extracted:** {len(va.get('keyframes', []))}",
            "",
        ])
        for kf in va.get("keyframes", []):
            lines.append(f"- Keyframe at `{kf.get('timestamp')}s`: {kf.get('label')}")
        lines.append("")

    # 8. Document & Slide Analysis
    if report["has_document"]:
        doc = report["document_analysis"]
        lines.extend([
            "---",
            "",
            "## 8. Document & Slide Analysis",
            f"- **Document File:** `{doc.get('document_name', report['document_filename'])}`",
            f"- **Total Pages/Slides:** {doc.get('total_pages', len(doc.get('pages', [])))}",
            "",
        ])
        for page in doc.get("pages", []):
            lines.append(f"### Slide/Page {page.get('page_number')}: {page.get('title')}")
            lines.append(f"{page.get('content')[:300]}...")
            if page.get("spoken_alignment"):
                lines.append(f"- **Spoken Discussion Alignment:** *{page.get('spoken_alignment')}*")
            lines.append("")

    # 9. Speaker Analysis
    if report["has_speakers"]:
        lines.extend([
            "---",
            "",
            "## 9. Speaker Participation Analysis",
            "| Speaker | Speaking Time | Turn Count | Share |",
            "| :--- | :--- | :--- | :--- |",
        ])
        for s in report["speakers"]:
            st = f"{s.get('speaking_time', 0.0)}s"
            tc = s.get("turns", "N/A")
            pct = f"{s.get('percentage', 0.0)}%"
            lines.append(f"| **{s.get('name')}** | {st} | {tc} | {pct} |")
        lines.append("")
    elif not report["has_speakers"] and report["transcript"]:
        lines.extend([
            "---",
            "",
            "## 9. Speaker Participation Analysis",
            "*Note: Distinct acoustic speaker diarization was not present in this session stream.*",
            "",
        ])

    # 10. Evidence & Sources
    if report["has_evidence"]:
        lines.extend([
            "---",
            "",
            "## 10. Evidence & Verifiable Sources",
            "| Claim Type | Intelligence Claim | Source | Verbatim Evidence Quote |",
            "| :--- | :--- | :--- | :--- |",
        ])
        for ev_item in report["evidence"]:
            ct = ev_item.get("claim_type", "Claim").capitalize()
            claim = ev_item.get("claim", "")[:60]
            src = ev_item.get("source_type", "transcript")
            if ev_item.get("timestamp"):
                src += f" [{ev_item.get('timestamp')}]"
            quote = ev_item.get("quote", "")[:100]
            lines.append(f"| {ct} | {claim} | `{src}` | \"{quote}\" |")
        lines.append("")

    lines.extend([
        "---",
        "",
        "*Report generated automatically by MeetingMind Dynamic Intelligence Engine.*",
    ])

    return "\n".join(lines)
