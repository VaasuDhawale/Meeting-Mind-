"""
Demo Data Generator: Generates realistic sample meeting video, audio, and agenda documents
specifically for testing and faculty evaluation.
"""

import math
import os
import struct
import subprocess
import wave
from pathlib import Path

import cv2
import numpy as np
import structlog

from app.config import settings

logger = structlog.get_logger()


def ensure_demo_media() -> tuple[str, str]:
    """
    Creates realistic demo video (with slides) and audio if they do not exist.
    Returns (video_path, document_path).
    """
    os.makedirs(settings.demo_dir, exist_ok=True)
    video_path = os.path.join(settings.demo_dir, "faculty_demo_meeting.mp4")
    agenda_path = os.path.join(settings.demo_dir, "faculty_demo_agenda.txt")
    wav_temp_path = os.path.join(settings.demo_dir, "temp_demo_audio.wav")

    # 1. Create realistic text document if not present
    if not os.path.exists(agenda_path):
        with open(agenda_path, "w", encoding="utf-8") as f:
            f.write(
                "DEMO DATA: Final Year Project Technical Review & Architecture Sync\n"
                "Attendees: Alex Rivera (Lead Architect), Priya Sharma (ML Engineer), David Chen (Fullstack)\n\n"
                "Meeting Agenda:\n"
                "1. Multimodal pipeline evaluation: OpenCV video keyframe extraction and audio track separation.\n"
                "2. Speech-to-text integration with OpenAI Whisper and local acoustic fallback.\n"
                "3. Extractive summarization using TextRank graph ranking and TF-IDF topic modeling.\n"
                "4. Action item extraction, assignee tagging, and priority classification.\n"
                "5. Automated PDF report generation with ReportLab.\n\n"
                "Session Notes & Transcript:\n"
                "Alex Rivera: Welcome everyone to the architecture review. Today we need to verify that our multimodal intelligence pipeline is working end to end.\n"
                "Priya Sharma: I have completed the OpenCV video frame difference algorithm. It accurately detects slide transitions and visual activity indexes.\n"
                "David Chen: How will we handle offline evaluation when external cloud API keys are not provided?\n"
                "Alex Rivera: The system automatically delegates to our local scikit-learn TF-IDF and TextRank pipeline for full offline reliability.\n"
                "David Chen: The backend API endpoints and React interface are ready. We must complete the integration testing before Friday.\n"
                "Alex Rivera: Excellent. We agreed that SQLite with async SQLAlchemy is our persistent store for the standalone faculty evaluation.\n"
                "Priya Sharma: Yes, and we decided to support both cloud LLMs and local scikit-learn algorithms for complete reliability without external dependencies.\n"
                "Alex Rivera: Perfect. Action item: Priya will prepare the benchmark evaluation report by tomorrow. David will finalize the PDF download and UI layout by Thursday.\n"
            )

    # 2. If video already exists, return
    if os.path.exists(video_path) and os.path.getsize(video_path) > 10000:
        return video_path, agenda_path

    logger.info("Generating realistic faculty demo video with slide transitions...")

    # Create synthetic audio track (8 seconds with modulated tones mimicking speech cadences)
    sample_rate = 16000
    duration_s = 8
    total_samples = sample_rate * duration_s
    with wave.open(wav_temp_path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for i in range(total_samples):
            t = i / sample_rate
            # Multi-frequency modulated speech-like wave
            val = (
                0.4 * math.sin(2 * math.pi * 220 * t)
                + 0.3 * math.sin(2 * math.pi * 440 * t)
                + 0.2 * math.sin(2 * math.pi * 880 * t)
            )
            # Add rhythmic pauses
            cadence = math.sin(2 * math.pi * 1.5 * t)
            if cadence < -0.3:
                val = 0.0
            sample = int(val * 16000)
            frames.extend(struct.pack("<h", sample))
        wav_file.writeframes(frames)

    # Generate slides using OpenCV
    width, height = 960, 540
    fps = 20
    slides_info = [
        ("DEMO DATA: SLIDE 1 - PROJECT OVERVIEW", "AI Multimodal Video Intelligence System", (30, 40, 60), 3 * fps),
        ("DEMO DATA: SLIDE 2 - ARCHITECTURAL PIPELINE", "OpenCV Video Analysis + Speech-to-Text + NLP", (20, 60, 40), 3 * fps),
        ("DEMO DATA: SLIDE 3 - ACTION ITEMS & RESULTS", "Decisions Approved | Report Generated", (60, 30, 20), 2 * fps),
    ]

    temp_video_silent = os.path.join(settings.demo_dir, "temp_silent.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(temp_video_silent, fourcc, fps, (width, height))

    for title, subtitle, bg_color, frame_count in slides_info:
        # Create base slide image
        slide_img = np.zeros((height, width, 3), dtype=np.uint8)
        slide_img[:] = bg_color

        # Draw decorative grid and banner
        cv2.rectangle(slide_img, (0, 0), (width, 80), (15, 23, 42), -1)
        cv2.putText(slide_img, title, (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

        # Draw content box
        cv2.rectangle(slide_img, (40, 120), (width - 40, height - 60), (255, 255, 255), -1)
        cv2.putText(slide_img, subtitle, (70, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (15, 23, 42), 2, cv2.LINE_AA)
        cv2.putText(slide_img, "Session: Engineering Review & Deliverables", (70, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (71, 85, 105), 1, cv2.LINE_AA)
        cv2.putText(slide_img, "Status: Active Demonstration Pipeline", (70, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (16, 185, 129), 2, cv2.LINE_AA)

        for _ in range(frame_count):
            writer.write(slide_img)

    writer.release()

    # Mux audio and video using ffmpeg
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        temp_video_silent,
        "-i",
        wav_temp_path,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-shortest",
        video_path,
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except Exception:
        # Fallback to silent video if muxing fails
        if os.path.exists(temp_video_silent):
            import shutil
            shutil.copyfile(temp_video_silent, video_path)

    # Cleanup temporary intermediates
    for temp_f in [temp_video_silent, wav_temp_path]:
        if os.path.exists(temp_f):
            try:
                os.remove(temp_f)
            except OSError:
                pass

    logger.info("Faculty demo media generated successfully", path=video_path)
    return video_path, agenda_path
