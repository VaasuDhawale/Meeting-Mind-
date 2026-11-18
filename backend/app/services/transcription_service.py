"""
Transcription Service: Multi-provider speech-to-text with Faster-Whisper (Local Neural Model),
OpenAI Whisper, AssemblyAI, and SpeechRecognition fallback.
Extracts full text and timestamped segments for rich evidence citation and screenshot alignment.
"""

import os
from typing import Any
import httpx
import numpy as np
import structlog
from app.config import settings

logger = structlog.get_logger()

# Global model cache to avoid reloading weights repeatedly
_faster_whisper_model = None


def format_seconds(seconds: float) -> str:
    """Format seconds into video-relative MM:SS or HH:MM:SS."""
    secs = int(max(0.0, round(seconds)))
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def load_audio_as_float32(audio_path: str) -> np.ndarray | None:
    """
    Read WAV audio into a float32 16kHz mono numpy array.
    Passing a numpy array directly to faster-whisper avoids PyAV version incompatibilities (av.open metadata_errors).
    """
    try:
        import scipy.io.wavfile as wavfile
        samplerate, data = wavfile.read(audio_path)
        if data.dtype == np.int16:
            audio = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            audio = data.astype(np.float32) / 2147483648.0
        elif data.dtype == np.uint8:
            audio = (data.astype(np.float32) - 128.0) / 128.0
        else:
            audio = data.astype(np.float32)

        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        if samplerate != 16000 and len(audio) > 0:
            import scipy.signal
            num_samples = int(len(audio) * 16000 / samplerate)
            audio = scipy.signal.resample(audio, num_samples).astype(np.float32)

        return audio
    except Exception as exc:
        logger.warning("Direct wavfile read failed, falling back to path", path=audio_path, error=str(exc))
        return None


def get_faster_whisper_model():
    """Lazy load faster-whisper model (preferring base for accuracy, falling back to tiny)."""
    global _faster_whisper_model
    if _faster_whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            try:
                logger.info("Initializing Faster-Whisper local model (base int8)")
                _faster_whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            except Exception as e_base:
                logger.info("Base model unavailable, falling back to tiny int8", error=str(e_base))
                _faster_whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        except Exception as exc:
            logger.warning("Failed to load Faster-Whisper model", error=str(exc))
            return None
    return _faster_whisper_model


async def transcribe_audio(
    audio_path: str,
    custom_api_key: str | None = None,
    preferred_provider: str | None = None,
) -> dict[str, Any]:
    """
    Transcribe audio using the primary configured provider or local neural Whisper fallback.
    Returns:
    {
        "text": str,
        "segments": [{"start": float, "end": float, "timestamp": str, "text": str}],
        "provider": str,
        "language": str,
        "quality_note": str | None
    }
    """
    openai_key = custom_api_key or settings.openai_api_key
    assemblyai_key = custom_api_key or settings.assemblyai_api_key

    # 1. OpenAI Whisper API
    if (preferred_provider == "openai" or not preferred_provider) and openai_key:
        try:
            logger.info("Transcribing audio using OpenAI Whisper API")
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            with open(audio_path, "rb") as audio_file:
                transcript_resp = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                )
            full_text = getattr(transcript_resp, "text", "")
            detected_lang = getattr(transcript_resp, "language", "en")
            segments = []
            if hasattr(transcript_resp, "segments") and transcript_resp.segments:
                for seg in transcript_resp.segments:
                    st = float(getattr(seg, "start", 0.0))
                    et = float(getattr(seg, "end", 0.0))
                    txt = getattr(seg, "text", "").strip()
                    if txt:
                        segments.append({
                            "start": round(st, 2),
                            "end": round(et, 2),
                            "timestamp": format_seconds(st),
                            "text": txt,
                        })

            if full_text:
                return {
                    "text": full_text.strip(),
                    "segments": segments,
                    "provider": "OpenAI Whisper (whisper-1)",
                    "language": detected_lang,
                    "quality_note": None,
                }
        except Exception as exc:
            logger.warning("OpenAI Whisper transcription failed, falling back", error=str(exc))

    # 2. AssemblyAI API
    if (preferred_provider == "assemblyai" or not preferred_provider) and assemblyai_key:
        try:
            logger.info("Transcribing audio using AssemblyAI")
            headers = {"authorization": assemblyai_key}
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                with open(audio_path, "rb") as f:
                    upload_resp = await http_client.post(
                        "https://api.assemblyai.com/v2/upload",
                        headers=headers,
                        content=f.read(),
                    )
                if upload_resp.status_code == 200:
                    audio_url = upload_resp.json().get("upload_url")
                    trans_req = await http_client.post(
                        "https://api.assemblyai.com/v2/transcript",
                        headers=headers,
                        json={"audio_url": audio_url, "speaker_labels": True},
                    )
                    trans_id = trans_req.json().get("id")
                    import asyncio
                    for _ in range(25):
                        await asyncio.sleep(2)
                        status_resp = await http_client.get(
                            f"https://api.assemblyai.com/v2/transcript/{trans_id}",
                            headers=headers,
                        )
                        data = status_resp.json()
                        if data.get("status") == "completed":
                            words = data.get("words", [])
                            segments = []
                            curr_seg = []
                            seg_start = 0.0
                            for w in words:
                                if not curr_seg:
                                    seg_start = w.get("start", 0) / 1000.0
                                curr_seg.append(w.get("text", ""))
                                if len(curr_seg) >= 15:
                                    seg_end = w.get("end", 0) / 1000.0
                                    segments.append({
                                        "start": round(seg_start, 2),
                                        "end": round(seg_end, 2),
                                        "timestamp": format_seconds(seg_start),
                                        "text": " ".join(curr_seg),
                                    })
                                    curr_seg = []
                            return {
                                "text": data.get("text", "").strip(),
                                "segments": segments,
                                "provider": "AssemblyAI",
                                "language": data.get("language_code", "en"),
                                "quality_note": None,
                            }
                        elif data.get("status") == "error":
                            break
        except Exception as exc:
            logger.warning("AssemblyAI transcription failed, falling back", error=str(exc))

    # 3. Faster-Whisper Local Neural Model (High performance, zero cost, exact timestamps)
    try:
        model = get_faster_whisper_model()
        if model is not None:
            logger.info("Transcribing with Faster-Whisper local neural model", audio_path=audio_path)
            # Use float32 numpy array to bypass PyAV version incompatibilities
            audio_input = load_audio_as_float32(audio_path)
            if audio_input is None:
                audio_input = audio_path

            segments_gen, info = model.transcribe(
                audio_input,
                beam_size=3,
                vad_filter=True,
                condition_on_previous_text=False,
            )
            segments = []
            text_parts = []
            for seg in segments_gen:
                clean_seg_text = seg.text.strip()
                # Exclude hallucinated repetitive single tokens or empty strings
                if clean_seg_text and len(clean_seg_text) > 1:
                    st = float(seg.start)
                    et = float(seg.end)
                    segments.append({
                        "start": round(st, 2),
                        "end": round(et, 2),
                        "timestamp": format_seconds(st),
                        "text": clean_seg_text,
                    })
                    text_parts.append(clean_seg_text)

            full_text = " ".join(text_parts).strip()
            if full_text:
                logger.info(
                    "Faster-Whisper transcription completed",
                    segments_count=len(segments),
                    words_count=len(full_text.split()),
                    language=info.language,
                )
                return {
                    "text": full_text,
                    "segments": segments,
                    "provider": "Faster-Whisper (Local Neural Model)",
                    "language": info.language,
                    "quality_note": None,
                }
    except Exception as exc:
        logger.warning("Faster-Whisper transcription encountered an error", error=str(exc))

    # 4. SpeechRecognition Fallback (chunked for long audio)
    logger.info("Using SpeechRecognition engine fallback")
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            dur = source.DURATION or 60.0
            segments = []
            text_parts = []
            # Process in 15-second chunks for better timestamp granularity
            chunk_len = 15.0
            curr_offset = 0.0
            while curr_offset < dur:
                audio_data = recognizer.record(source, duration=min(chunk_len, dur - curr_offset))
                chunk_start = curr_offset
                curr_offset += chunk_len
                try:
                    chunk_text = recognizer.recognize_google(audio_data)
                    if chunk_text and chunk_text.strip():
                        st = max(0.0, chunk_start)
                        et = min(curr_offset, dur)
                        segments.append({
                            "start": round(st, 2),
                            "end": round(et, 2),
                            "timestamp": format_seconds(st),
                            "text": chunk_text.strip(),
                        })
                        text_parts.append(chunk_text.strip())
                except Exception:
                    pass

            full_text = " ".join(text_parts).strip()
            if full_text:
                return {
                    "text": full_text,
                    "segments": segments,
                    "provider": "SpeechRecognition (Acoustic Chunks)",
                    "language": "en",
                    "quality_note": "Acoustic chunked fallback recognition.",
                }
    except Exception as exc:
        logger.warning("Local speech recognition fallback encountered an issue", error=str(exc))

    return {
        "text": "",
        "segments": [],
        "provider": "Local Audio Processor",
        "language": "en",
        "quality_note": "No intelligible speech detected in vocal stream.",
    }
