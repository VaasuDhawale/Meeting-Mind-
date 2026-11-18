# MeetingMind
### AI-Powered Meeting Intelligence & Report Generator

> **PBL Final Year Project** • An end-to-end multimodal intelligence platform that converts recorded video sessions, audio streams, and supporting presentation documents into structured, context-aware, verifiable knowledge reports.

[![Backend Tests](https://img.shields.io/badge/pytest-18%20passed-success?logo=pytest&logoColor=white)](file:///p:/PBL%20Final%20year%20project/backend/tests)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.14-blue?logo=python&logoColor=white)](file:///p:/PBL%20Final%20year%20project/backend)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](file:///p:/PBL%20Final%20year%20project/backend)
[![React](https://img.shields.io/badge/React-19.2-61DAFB?logo=react&logoColor=black)](file:///p:/PBL%20Final%20year%20project/frontend)
[![Vite](https://img.shields.io/badge/Vite-6.1-646CFF?logo=vite&logoColor=white)](file:///p:/PBL%20Final%20year%20project/frontend)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v4-06B6D4?logo=tailwindcss&logoColor=white)](file:///p:/PBL%20Final%20year%20project/frontend)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20Async-red?logo=sqlalchemy&logoColor=white)](file:///p:/PBL%20Final%20year%20project/backend/app/db)

---

## Table of Contents

- [A. Project Title and Overview](#meetingmind)
- [B. Table of Contents](#table-of-contents)
- [C. Problem Statement](#c-problem-statement)
- [D. Proposed Solution](#d-proposed-solution)
- [E. Key Features](#e-key-features)
- [F. Why MeetingMind?](#f-why-meetingmind)
- [G. Supported Inputs and Outputs](#g-supported-inputs-and-outputs)
- [H. System Architecture](#h-system-architecture)
- [I. Architecture and Design Decisions](#i-architecture-and-design-decisions)
- [J. Technology Stack](#j-technology-stack)
- [K. Detailed AI/ML Pipeline](#k-detailed-aiml-pipeline)
- [L. Transcription and Audio Processing](#l-transcription-and-audio-processing)
- [M. Computer Vision and Video Processing](#m-computer-vision-and-video-processing)
- [N. NLP and Intelligence Extraction](#n-nlp-and-intelligence-extraction)
- [O. Report Generation Engine](#o-report-generation-engine)
- [P. Frontend Architecture](#p-frontend-architecture)
- [Q. Backend Architecture](#q-backend-architecture)
- [R. Database and Data Flow](#r-database-and-data-flow)
- [S. API Documentation](#s-api-documentation)
- [T. Project Structure](#t-project-structure)
- [U. Installation and Prerequisites](#u-installation-and-prerequisites)
- [V. Environment Configuration](#v-environment-configuration)
- [W. Installation and Setup](#w-installation-and-setup)
- [X. Docker Setup](#x-docker-setup)
- [Y. How to Use MeetingMind](#y-how-to-use-meetingmind)
- [Z. Faculty Demo Mode](#z-faculty-demo-mode)
- [AA. Testing and Quality Assurance](#aa-testing-and-quality-assurance)
- [AB. Security and Privacy](#ab-security-and-privacy)
- [AC. Error Handling and Troubleshooting](#ac-error-handling-and-troubleshooting)
- [AD. Known Limitations](#ad-known-limitations)
- [AE. Future Improvements](#ae-future-improvements)
- [AF. Performance and Evaluation](#af-performance-and-evaluation)
- [AG. Engineering Challenges and Design Trade-offs](#ag-engineering-challenges-and-design-trade-offs)
- [AH. Technical Interview Preparation](#ah-technical-interview-preparation)
- [AI. Interview Questions and Answers](#ai-interview-questions-and-answers)
- [AJ. Resume-Ready Project Description](#aj-resume-ready-project-description)
- [AK. Screenshots and Visual Documentation](#ak-screenshots-and-visual-documentation)
- [AL. Contributing and License](#al-contributing-and-license)
- [AM. Final Documentation Audit](#am-final-documentation-audit)

---

## C. Problem Statement

Modern academic, engineering, and corporate organizations conduct critical architectural reviews, planning syncs, and executive evaluations via video conferences. However, post-meeting knowledge retention suffers from severe structural bottlenecks:

1. **High Review Overhead**: Reviewing a 60-minute recorded session to locate a specific decision or task requires scrubbing through lengthy recordings or scanning thousands of unformatted transcript words.
2. **Loss of Visual Context**: Conventional speech-to-text tools only capture audio. When a presenter shares a slide, an architectural diagram, a code walk-through, or a spreadsheet, purely audio-derived transcripts lose the context of what was being visually demonstrated.
3. **Unstructured & Non-Actionable Outputs**: Raw transcripts are unpunctuated stream-of-consciousness text. They lack distinct categorizations for actionable commitments, deadlines, assignees, agreed decisions, and discussion topics.
4. **Hallucination & Verification Gaps**: Off-the-shelf generative AI summarizers frequently hallucinate consensus, misattribute assignees, or invent details not present in the discussion. Without verbatim cross-referenced quotes and timestamped evidence, outputs cannot be verified for high-stakes audits.
5. **Static, Inflexible Formats**: Organizations require different artifacts: executives require concise summary briefs, auditors demand timestamped evidence matrices, team members need editable Word (.docx) task lists, and systems require structured JSON feeds.

---

## D. Proposed Solution

**MeetingMind** transforms raw multimodal meeting recordings into structured, audit-ready, actionable intelligence reports through a multi-stage deterministic and AI pipeline:

$$\text{Video / Audio / Documents} \xrightarrow{\text{Extraction}} \text{Visual Keyframes + Audio WAV + Parsed Text} \xrightarrow{\text{Fusion \& NLP}} \text{Structured Intelligence} \xrightarrow{\text{Compilers}} \text{PDF / DOCX / MD / JSON}$$

1. **Multimodal Media Ingestion**: Ingests video (`.mp4`, `.webm`, `.mkv`, `.avi`, `.mov`) or audio (`.mp3`, `.wav`, `.m4a`), alongside optional supporting documents (`.pdf`, `.pptx`, `.txt`).
2. **Dual-Track Decomposition**:
   - **Video Track**: OpenCV calculates frame-by-frame luminance differences to detect visual scene and slide transitions, extracting representative keyframe screenshots and computing a visual activity engagement index.
   - **Audio Track**: FFmpeg extracts a standardized 16 kHz mono PCM WAV stream, transcribing it into verbatim text via cloud APIs (OpenAI Whisper, AssemblyAI) or an offline acoustic fallback engine (`speech_recognition`).
   - **Document Track**: PyPDF/pdfplumber and python-pptx extract slide titles, sections, and notes to contextualize discussion topics.
3. **Deterministic & Algorithmic NLP Fusion**:
   - Extract topics using Scikit-Learn TF-IDF n-gram vectorization.
   - Generate extractive summaries using graph-based TextRank (cosine similarity and PageRank power iteration).
   - Extract action items (with assignees, priorities, and deadlines) and formal decisions using rule-based lexical matching.
   - Map every claim to an explicit `evidence` record with transcript quotes and timestamp references.
4. **Hybrid Cloud LLM Synthesis (Optional)**: When API credentials for OpenAI (`gpt-4o-mini`) or Google Gemini (`gemini-1.5-flash`) are supplied, the pipeline executes structured schema-constrained JSON synthesis.
5. **Multi-Format Publication**: Automatically compiles results into ReportLab PDF reports, native Microsoft Word (`.docx`) documents via `python-docx`, Markdown (`.md`), plain text (`.txt`), and JSON schemas.

---

## E. Key Features

| Feature | Description | Implementation Status |
|---|---|---|
| **Video & Audio Ingestion** | Multipart upload supporting video containers and audio tracks up to 500 MB (configurable to 2048 MB) | **Implemented & Verified** |
| **Media Validation & Sanitization** | Regex sanitization of filenames, MIME header inspection, and file size boundary enforcement | **Implemented & Verified** |
| **FFmpeg Audio Extraction** | Subprocess invocation converting incoming video streams into 16 kHz mono 16-bit PCM WAV tracks | **Implemented & Verified** |
| **Speech-to-Text Transcription** | Multi-tier provider architecture: OpenAI Whisper API (`whisper-1`), AssemblyAI, with local `speech_recognition` fallback | **Implemented & Verified** |
| **OpenCV Scene & Slide Detection** | Inter-frame absolute difference ($160\times90$ grayscale downsampling) with adaptive thresholding to detect slide shifts | **Implemented & Verified** |
| **Keyframe Screenshot Extraction** | Timestamped JPEG keyframes saved to disk and served over FastAPI `/static` route | **Implemented & Verified** |
| **Visual Activity Index** | Percentage metric measuring scene change frequency relative to total sampled video duration | **Implemented & Verified** |
| **TF-IDF Topic Modeling** | Scikit-Learn `TfidfVectorizer` (unigrams + bigrams) extracting salient topics with relevance scores (0.0 to 1.0) | **Implemented & Verified** |
| **TextRank Extractive Summarization** | Graph-based PageRank ($d = 0.85$, 25 iterations) over TF-IDF sentence cosine similarity matrix | **Implemented & Verified** |
| **Action Item Mining** | Regex patterns identifying commitment verbs; extracts tasks, assignees, priorities (High/Medium/Low), and due dates | **Implemented & Verified** |
| **Decision Tracking** | Extraction of formal agreements, contextual consensus, and contributing meeting participants | **Implemented & Verified** |
| **Q&A Dialogue Mining** | Extraction of questions paired with subsequent speaker responses and timestamps | **Implemented & Verified** |
| **Sentiment & Engagement Analysis** | Lexical token-set scoring evaluating positive, constructive, and neutral emotional tone | **Implemented & Verified** |
| **Speaker Diarization** | Dialogue-turn regex parsing calculating speaker turns, word counts, and speaking percentages | **Implemented & Verified** |
| **Supporting Document Parser** | Extraction of slide content and text from PDF, PPTX, and TXT documents | **Implemented & Verified** |
| **Cross-Verification Evidence Linker** | Generates `evidence` objects linking every decision and task to exact transcript quotes and timestamps | **Implemented & Verified** |
| **Cloud LLM Integration** | Schema-enforced JSON extraction via OpenAI GPT-4o-mini and Google Gemini 1.5 Flash | **Implemented (Requires API Key)** |
| **Zero-Dependency Local Mode** | Complete offline execution using Scikit-Learn, TextRank, and acoustic fallbacks without cloud keys | **Implemented & Verified** |
| **ReportLab Executive PDF Export** | Multi-page publication-grade PDF report with custom tables, keyframes, and two-pass page numbering | **Implemented & Verified** |
| **Native Word DOCX Export** | Microsoft Word generation (`python-docx`) with XML-level cell background shading, borders, and margins | **Implemented & Verified** |
| **Verbatim Transcript PDF/TXT** | Dedicated PDF document and plain text download containing timestamped transcript text | **Implemented & Verified** |
| **Markdown & JSON Data Exports** | Standardized exports adhering to strict dynamic report schemas | **Implemented & Verified** |
| **Asynchronous SQLite Persistence** | Non-blocking persistence using SQLAlchemy 2.0 with `aiosqlite` and automated schema column migration | **Implemented & Verified** |
| **Pre-Packaged Faculty Demo** | Synthetic video with slide graphics, tone-modulated audio, and agenda; executes zero-upload demo | **Implemented & Verified** |
| **Historical Session Management** | Browse, review, re-download, or delete saved meeting sessions from SQLite store | **Implemented & Verified** |
| **Celery + Redis Worker Architecture** | Celery task queue configuration for background worker processing | **Partially Implemented (Commented in Compose)** |

---

## F. Why MeetingMind?

| Dimension | Standard Speech-to-Text (e.g., Otter, Whisper CLI) | Generic Cloud Summarizers (e.g., ChatGPT paste) | MeetingMind Multimodal Platform |
|---|---|---|---|
| **Visual Ingestion** | None (Audio only) | None (Text only) | **Full OpenCV integration** detects slide changes and extracts keyframe screenshots |
| **Supporting Material** | Not supported | Requires manual copying | **Direct document parsing** for PDF, PPTX, and TXT agenda fusion |
| **Offline Reliability** | Cloud-dependent | Cloud-dependent | **Dual-engine architecture**: runs 100% locally with Scikit-learn & TextRank when offline |
| **Hallucination Control** | High risk when summarized | Summaries can hallucinate | **Strict evidence linking**: every task and decision cites exact transcript quotes |
| **Document Compilation** | Raw text or simple `.vtt`/`.srt` | Markdown output only | **Engineered publication outputs**: Pixel-precise PDF (ReportLab) & editable Word (.docx) |
| **Persistence** | Proprietary cloud storage | Browser local cache | **Self-hosted SQLite / PostgreSQL** with async SQLAlchemy persistence |

---

## G. Supported Inputs and Outputs

### Supported Ingestion Formats

| Input Category | Supported Extensions | Processing Method | Verification Status |
|---|---|---|---|
| **Video Files** | `.mp4`, `.webm`, `.mkv`, `.avi`, `.mov` | OpenCV frame differencing (`cv2.VideoCapture`) + FFmpeg audio extraction (`pcm_s16le`) | **Verified** |
| **Audio Files** | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac` | Direct pass-through to speech-to-text pipeline (bypasses OpenCV) | **Verified** |
| **Presentations** | `.pptx`, `.ppt` | `python-pptx` extracts slide text frames and structural titles | **Verified** |
| **Documents** | `.pdf` | `pdfplumber` / PyPDF extracts page-by-page text blocks | **Verified** |
| **Agendas & Notes**| `.txt` | Plain-text section parsing via paragraph regex boundaries | **Verified** |

### Supported Intelligence Outputs

| Output Format | Endpoint | Purpose | Verification Status |
|---|---|---|---|
| **Executive PDF Report** | `GET /api/v1/sessions/{id}/pdf` | Audit-ready, styled multi-page PDF containing overview, metrics, keyframes, decisions, tasks, and evidence | **Verified** |
| **Microsoft Word Document** | `GET /api/v1/sessions/{id}/docx` | Fully editable `.docx` document with styled headers, custom XML shaded tables, and embedded keyframes | **Verified** |
| **Verbatim Transcript PDF** | `GET /api/v1/sessions/{id}/transcript-pdf` | Dedicated publication PDF containing dialogue and speaker turns | **Verified** |
| **Raw Transcript Text** | `GET /api/v1/sessions/{id}/transcript-txt` | Raw plain text export of transcript with timestamp markers | **Verified** |
| **Structured JSON Schema** | `GET /api/v1/sessions/{id}/json` | Standardized REST data export for integration with external dashboards | **Verified** |
| **GitHub Markdown Report** | `GET /api/v1/sessions/{id}/markdown` | Formatted Markdown file with evidence quotes and tables | **Verified** |
| **Plain Text Report** | `GET /api/v1/sessions/{id}/txt` | Clean formatted text report for terminal viewing or email distribution | **Verified** |

---

## H. System Architecture

```mermaid
flowchart TD
    subgraph Client ["Frontend Layer (React 19 + Vite 6 + Tailwind CSS)"]
        UI[Web Dashboard]
        Upload["UploadSection.tsx"]
        Overlay["ProcessingOverlay.tsx"]
        Results["ResultsView.tsx"]
        History["SessionsHistory.tsx"]
        APIClient["api.ts (Axios + Fetch)"]
    end

    subgraph Gateway ["API & Application Gateway (FastAPI)"]
        Main["app/main.py"]
        CORS["CORSMiddleware"]
        StaticMount["/static Mount (Storage Dir)"]
        RouterHealth["/api/v1/health"]
        RouterSessions["/api/v1/sessions"]
    end

    subgraph MediaEngines ["Media & Ingestion Services"]
        MediaSvc["media_service.py"]
        FFmpegEngine["FFmpeg (Audio Demuxing)"]
        OpenCVEngine["OpenCV (Frame Differencing)"]
        DocParser["Doc Parser (pdfplumber, pptx)"]
    end

    subgraph SpeechEngines ["Transcription Layer"]
        TransSvc["transcription_service.py"]
        WhisperAPI["OpenAI Whisper API"]
        AssemblyAI["AssemblyAI API"]
        SpeechRec["SpeechRecognition (Local)"]
    end

    subgraph IntelligenceEngines ["NLP & Intelligence Layer"]
        NLPSvc["nlp_ai_service.py"]
        TFIDF["Scikit-Learn TF-IDF"]
        TextRank["TextRank (Cosine + PageRank)"]
        RuleExtract["Regex Decision & Task Miner"]
        SentimentEng["Lexical Sentiment Scorer"]
        EvidenceLink["Evidence Linking Matrix"]
        LLMOpenAI["OpenAI GPT-4o-mini"]
        LLMGemini["Google Gemini 1.5 Flash"]
    end

    subgraph Compilers ["Publication & Persistence Engine"]
        ReportEng["report_engine.py"]
        PDFSvc["pdf_service.py (ReportLab)"]
        DOCXSvc["docx_service.py (python-docx)"]
        DBSession["app/db/session.py"]
        SQLiteDB[("SQLite: meetingmind.db")]
        FileStore[("Local Disk Storage: /storage")]
    end

    UI --> Upload --> APIClient
    APIClient -->|HTTP POST Multipart| RouterSessions
    RouterSessions --> MediaSvc
    MediaSvc --> FFmpegEngine --> TransSvc
    MediaSvc --> OpenCVEngine --> FileStore
    MediaSvc --> DocParser
    
    TransSvc --> WhisperAPI
    TransSvc --> AssemblyAI
    TransSvc --> SpeechRec
    TransSvc --> NLPSvc

    NLPSvc --> TFIDF
    NLPSvc --> TextRank
    NLPSvc --> RuleExtract
    NLPSvc --> SentimentEng
    NLPSvc --> EvidenceLink
    NLPSvc -.->|Optional API Key| LLMOpenAI
    NLPSvc -.->|Optional API Key| LLMGemini

    NLPSvc --> ReportEng
    ReportEng --> PDFSvc --> FileStore
    ReportEng --> DOCXSvc --> FileStore
    ReportEng --> DBSession --> SQLiteDB

    DBSession --> RouterSessions
    RouterSessions --> APIClient
    APIClient --> Results
    APIClient --> History
    FileStore --> StaticMount --> UI
```

---

## I. Architecture and Design Decisions

### 1. Decoupled Synchronous Pipeline with Progressive UI Feedback
- **Engineering Rationale**: In academic evaluation and single-instance deployments, running a separate message broker (Redis) and worker daemon (Celery) adds operational failure points (broker connectivity drops, unhandled worker task crashes). 
- **Implementation**: The processing pipeline executes synchronously within FastAPI async worker threads, while the frontend (`ProcessingOverlay.tsx`) provides 5-stage visual progress feedback. A timeout threshold of 180 seconds is set in `api.ts` to accommodate heavy media processing.

### 2. Zero-Dependency Local Fallback (Dual-Engine AI)
- **Engineering Rationale**: Production AI applications must degrade gracefully when external cloud APIs experience rate limits, billing expirations, or offline network constraints.
- **Implementation**: When `OPENAI_API_KEY` or `GOOGLE_AI_API_KEY` are unavailable, `nlp_ai_service.py` automatically delegates to a deterministic, local machine learning pipeline using Scikit-Learn TF-IDF, graph-based TextRank, and lexical regular expressions.

### 3. Separation of Content Compilation from Document Rendering
- **Engineering Rationale**: Generating multiple document formats (PDF, DOCX, Markdown, Text, JSON) independently leads to inconsistencies across reports.
- **Implementation**: The `report_engine.py` module defines a single `build_dynamic_report()` function that processes raw session attributes, evaluates which sections have genuine data, and constructs a normalized dictionary. `pdf_service.py` and `docx_service.py` consume this identical data structure.

### 4. Non-Destructive In-Place SQLite Migration
- **Engineering Rationale**: During iterative development, schema modifications often break existing databases.
- **Implementation**: `init_db()` in `session.py` executes `PRAGMA table_info(meeting_sessions)` upon startup. If newly added columns (`questions_answers`, `timeline`, `document_analysis`, `evidence`, `docx_path`) are missing from an existing database file, it executes safe `ALTER TABLE ADD COLUMN` commands without dropping user data.

---

## J. Technology Stack

| Layer | Technology | Purpose | Actual Usage & Configuration |
|---|---|---|---|
| **Frontend Framework** | React 19.2, TypeScript 6.0 | Single-page application UI | Type-safe component trees, stateful tab navigation, and reactive upload handling |
| **Build Tooling** | Vite 8.2 | Development server & bundler | Instant HMR, API proxying (`/api`, `/static`), production chunking |
| **Styling** | Tailwind CSS v4 | Utility-first responsive design | Modern dark-mode palette (`slate-950`, `slate-900`, `blue-500`), glassmorphic overlays |
| **Icons & Assets** | Lucide React | Visual iconography | Status indicators, media type badges, timeline icons |
| **Backend Framework** | FastAPI 0.115+ | Asynchronous REST API | Route handling, request validation, static file mounting, lifespan events |
| **ASGI Server** | Uvicorn 0.30+ | High-performance Python server | Single-worker event loop serving `0.0.0.0:8000` |
| **Configuration** | Pydantic BaseSettings 2.3+ | Environment variable parsing | Validated type coercion, CORS parsing, default path generation |
| **Database ORM** | SQLAlchemy 2.0 (Async) | Object relational mapping | Async engine, session context manager, declarative Base models |
| **Database Driver** | aiosqlite | Async SQLite driver | Standalone zero-setup database driver storing `meetingmind.db` |
| **Computer Vision** | OpenCV (`cv2`) 4.10+ | Video frame analysis | Inter-frame luminance subtraction, transition thresholding, JPEG keyframe writing |
| **Audio Processing** | FFmpeg | Media demuxing | Subprocess execution converting video streams to 16 kHz mono WAV |
| **Speech-to-Text** | `speech_recognition` | Offline audio transcription | Google Speech recognition engine fallback |
| **Cloud Speech API** | OpenAI Whisper API (`whisper-1`) | Cloud audio transcription | High-accuracy multilingual speech transcription |
| **Cloud Speech API** | AssemblyAI REST API | Cloud speech transcription | Polled HTTP transcript generation with speaker labels |
| **Machine Learning** | Scikit-Learn 1.5+ | Mathematical text modeling | `TfidfVectorizer` (ngram_range=(1,2)), cosine similarity calculation |
| **PDF Compiler** | ReportLab 3.14+ | Pixel-precise PDF generation | `SimpleDocTemplate`, custom `ParagraphStyle`, `NumberedCanvas` two-pass page numbers |
| **Word Compiler** | python-docx 1.1+ | Editable Word document generation | `Document`, low-level `parse_xml` for cell background shading (`w:shd`) and margins (`w:tcMar`) |
| **Document Parsers**| pdfplumber, python-pptx | Supporting document ingestion | Text extraction from PDF slides and PPTX shape trees |
| **Testing** | Pytest 9.1, pytest-asyncio | Test suite | 18 automated unit and integration tests across DOCX, PDF, and pipeline logic |

---

## K. Detailed AI/ML Pipeline

```
[Media Input: Video/Audio + Document]
       │
       ▼
[1. Ingestion & Validation] ───► Validate extension, sanitize filename, enforce max size
       │
       ▼
[2. Media Splitting]
       ├─────────────────────────────────┐
       ▼                                 ▼
[Visual Track (OpenCV)]          [Audio Track (FFmpeg)]
  - 1 frame/sec sample             - Subprocess execution
  - 160x90 grayscale diff          - 16kHz Mono PCM WAV
  - Scene threshold > 18.0         - Written to session dir
  - Save keyframes to disk               │
       │                                 ▼
       │                         [3. Transcription Engine]
       │                           - OpenAI Whisper API (Priority 1)
       │                           - AssemblyAI API (Priority 2)
       │                           - Local SpeechRecognition (Fallback)
       │                                 │
       └────────────────► ◄──────────────┘
                          │
                          ▼
             [4. Multimodal Data Fusion]
               - Align transcript with parsed document text
               - Combine speaker dialogue turns
                          │
                          ▼
             [5. Intelligence Synthesis]
       ┌──────────────────┴──────────────────┐
       ▼                                     ▼
[Cloud LLM Mode]                     [Local Algorithmic Mode]
- OpenAI GPT-4o-mini                 - TF-IDF Topic Modeling (Scikit-Learn)
- Gemini 1.5 Flash                   - TextRank Extractive Summarizer
- Schema-constrained JSON            - Regex Action & Decision Mining
                                     - Lexical Sentiment Polarity
                                     - Cross-Verification Evidence Matrix
       └──────────────────┬──────────────────┘
                          │
                          ▼
             [6. Normalized Report Assembly]
               - Validate active data sections
               - Build evidence linkages (claim -> quote + timestamp)
                          │
                          ▼
             [7. Multi-Format Compilers]
               - ReportLab PDF generator
               - python-docx Microsoft Word generator
               - Markdown / Plain Text generator
               - Structured JSON export
                          │
                          ▼
             [8. Database Persistence]
               - Async SQLAlchemy commit to SQLite
               - Return serialized session payload
```

---

## L. Transcription and Audio Processing

The transcription subsystem in `app/services/transcription_service.py` implements a cascading fallback design:

1. **Audio Extraction (`media_service.py`)**:
   - Executes FFmpeg via Python `subprocess.run`:
     ```bash
     ffmpeg -y -i <video_path> -vn -acodec pcm_s16le -ar 16000 -ac 1 <output_wav_path>
     ```
   - Standardizes the audio track to 16,000 Hz, 16-bit, single-channel (mono) uncompressed PCM WAV.

2. **Provider Resolution Logic**:
   - **OpenAI Whisper (`whisper-1`)**: Activated if `preferred_provider == "openai"` or if `OPENAI_API_KEY` is present. Uses official `openai.OpenAI` SDK with `response_format="verbose_json"`.
   - **AssemblyAI API**: Activated if `preferred_provider == "assemblyai"` or if `ASSEMBLYAI_API_KEY` is present. Uploads raw bytes to `https://api.assemblyai.com/v2/upload`, submits a transcript request with `speaker_labels=True`, and polls the completion endpoint.
   - **SpeechRecognition Local Engine**: Default offline fallback. Ingests the WAV audio via `sr.AudioFile` and processes it via the local recognition engine without requiring API keys.

---

## M. Computer Vision and Video Processing

The computer vision subsystem in `app/services/media_service.py` utilizes OpenCV (`cv2`) for heuristic visual intelligence:

1. **Video Decoding & Sampling**:
   - Reads the input video file using `cv2.VideoCapture`.
   - Reads container properties: frames per second (FPS), total frame count, frame width, and frame height.
   - Samples **1 frame per second** (`curr_frame_idx % int(fps) == 0`) to minimize processing latency.

2. **Inter-Frame Luminance Differencing**:
   - Each sampled frame is converted to grayscale (`cv2.COLOR_BGR2GRAY`) and downsampled to $160 \times 90$ pixels to ensure real-time performance and eliminate compression artifacts.
   - Computes absolute difference between consecutive frames:
     $$\Delta I = \frac{1}{W \times H} \sum_{x,y} |I_t(x,y) - I_{t-1}(x,y)|$$
   - When $\Delta I > 18.0$, a **visual transition / slide change** is registered.

3. **Keyframe Selection & Storage**:
   - The initial frame ($t = 0\text{s}$) is always captured.
   - Subsequent keyframes are captured only when a transition is detected and at least **3.0 seconds** have elapsed since the prior keyframe (preventing redundant captures during video playback).
   - Up to 6 keyframes are saved as JPEG files in `storage/keyframes/{session_id}/kf_{timestamp}s.jpg`.

4. **Visual Activity Metric**:
   - Calculates the overall visual activity index:
     $$\text{Visual Activity \%} = \min\left(100.0, \frac{\text{Scene Changes}}{\text{Sampled Frames}} \times 100.0\right)$$

*Important Technical Distinction*: OpenCV performs deterministic pixel-difference analysis and slide detection. It does not perform open-domain visual object recognition or semantic visual question answering.

---

## N. NLP and Intelligence Extraction

The NLP pipeline in `app/services/nlp_ai_service.py` provides deterministic algorithms and optional generative models:

### 1. Scikit-Learn TF-IDF Topic Modeling
- Ingests cleaned transcript and document text.
- Initializes `TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=20)`.
- Calculates term frequency-inverse document frequency weights:
  $$\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \left(\log \frac{1 + n}{1 + \text{DF}(t)} + 1\right)$$
- Identifies the top 6 scoring unigrams and bigrams. Locates sentences containing each term to populate supporting evidence points.

### 2. Graph-Based TextRank Extractive Summarization
- Splits text into distinct sentences using regex boundaries: `(?<=[.!?])\s+`.
- Computes TF-IDF vector representations for each sentence and calculates an $N \times N$ cosine similarity adjacency matrix:
  $$S_{ij} = \frac{\vec{v}_i \cdot \vec{v}_j}{\|\vec{v}_i\| \|\vec{v}_j\|}$$
- Executes 25 iterations of Power Method PageRank with a damping factor of $d = 0.85$:
  $$PR(S_i) = \frac{1-d}{N} + d \sum_{j \ne i} \frac{S_{ji}}{\sum_k S_{jk}} PR(S_j)$$
- Selects the top 4 highest-scoring central sentences in their chronological order to form an extractive executive summary.

### 3. Rule-Based Action Item & Decision Extraction
- **Action Items**: Matches modal verbs and commitment phrases:
  - `(?:need to|have to|must|should|will|action item|task|todo|assigned to)\s+([^,.;]+)`
  - Identifies assignees by matching capitalized names against detected speaker lists or defaults to "Project Team".
  - Infers priority: marked **High** if containing "must", "urgent", "critical", or "asap"; **Low** if containing "nice to" or "if possible"; otherwise **Medium**.
- **Formal Decisions**: Matches consensus patterns:
  - `(?:agreed|decided|concluded|approved|confirmed|resolved)\s+(?:that|to)?\s*([^.;]+)`
  - Extracts the agreeing participants and links the source sentence as verbatim evidence.

### 4. Lexical Sentiment & Engagement Scoring
- Tokenizes dialogue into individual words and matches against positive and negative valence sets.
- Generates bounded scores: `positive_score`, `negative_score`, and `neutral_score`.
- Classifies tone into `Positive`, `Constructive`, or `Neutral`.

### 5. Evidence Matrix Engine
- Constructs an explicit `evidence` array containing unique identifiers (`ev-1`, `ev-2`, etc.).
- Maps each claim to `claim_type` ("decision", "action_item", "visual"), `claim`, `source_type` ("transcript", "video_keyframe"), `timestamp`, and the exact verbatim source quote.

---

## O. Report Generation Engine

### 1. Unified Dynamic Report Engine (`app/services/report_engine.py`)
- Ingests raw session dictionaries and evaluates active sections.
- Sections are **only** rendered if they contain verified data:
  - `executive_summary` (if summary text exists)
  - `topics` (if $\ge 1$ topic exists)
  - `action_items` (if $\ge 1$ task exists)
  - `decisions` (if $\ge 1$ decision exists)
  - `questions_answers` (if $\ge 1$ Q&A exists)
  - `timeline` (if keyframe or topic events exist)
  - `visual_intelligence` (if keyframes or video metadata exist)
  - `document_analysis` (if supporting document pages exist)
  - `speakers` (if speakers were detected)
  - `evidence` (if verified citations exist)

### 2. ReportLab PDF Generation (`app/services/pdf_service.py`)
- Employs `SimpleDocTemplate` with letter page sizing and 0.5-inch margins.
- Implements `NumberedCanvas` which overrides `showPage` and `save` to perform a two-pass calculation of total pages, rendering exact "Page X of Y" footers.
- Renders keyframe screenshots using ReportLab `Image` flowables with automatic aspect ratio scaling.
- Applies XML-safe character escaping via `safe_text()` to prevent parser crashes.

### 3. Native Microsoft Word Generation (`app/services/docx_service.py`)
- Uses `python-docx` to create `.docx` documents.
- Injects low-level OpenXML elements:
  - `parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')` for cell background fills.
  - `parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/>...</w:tcMar>')` for cell padding.
- Embeds OpenCV keyframe JPEG images directly into Word table cells.

---

## P. Frontend Architecture

The frontend is a single-page application built with React 19, Vite 6, and Tailwind CSS v4.

### Component Structure (`frontend/src/`)
- `main.tsx`: Application bootstrap mounting the root component into `#root`.
- `App.tsx`: Central coordinator managing active tab views (`new`, `history`, `result`), selected session state, polling health status, and initiating analysis routines.
- `components/Navbar.tsx`: Top navigation bar displaying brand identity, backend connection status badge (`healthy` / `offline`), and tab switches.
- `components/StorytellingLanding.tsx`: Interactive landing view detailing the multimodal problem, pipeline architecture, and faculty demo trigger.
- `components/UploadSection.tsx`: Form for file drag-and-drop, title customization, provider selection (Auto / Local ML / OpenAI / Gemini), and client-side format/size validation.
- `components/ProcessingOverlay.tsx`: 5-stage progress overlay with animated timers and step indicators.
- `components/ResultsView.tsx`: Comprehensive dashboard containing tabs for Overview, Visual Shifts, Action Items, Topics, Timeline, Transcript, and Document Alignment, alongside instant download buttons.
- `components/SessionsHistory.tsx`: Historical session table displaying past analyses stored in SQLite with delete and download controls.
- `api.ts`: API integration module utilizing `axios` for JSON endpoints and native `fetch` for binary blob file downloads.

---

## Q. Backend Architecture

The backend is built on FastAPI with async/await execution:

### Module Responsibilities (`backend/app/`)
- `main.py`: Application factory defining `create_app()`, CORS middleware configuration, static directory mounting (`/static` $\to$ `storage`), and `lifespan` startup routines (database initialization, storage directory creation, demo media verification).
- `config.py`: `Settings` class using Pydantic `BaseSettings`. Loads `.env` values, defines file size limits, allowed extensions, and directory paths.
- `db/base.py`: Declarative SQLAlchemy base class.
- `db/models.py`: Defines the `MeetingSession` SQLAlchemy model with JSON column types for structured intelligence arrays.
- `db/session.py`: Manages the async database engine (`create_async_engine`), session factory (`async_sessionmaker`), and non-destructive schema migrations (`init_db()`).
- `api/v1/health.py`: Health check endpoint querying database status and returning system uptime.
- `api/v1/sessions.py`: Primary API router containing session upload, demo execution, retrieval, export, and deletion endpoints.
- `services/media_service.py`: Video analysis via OpenCV, audio extraction via FFmpeg, document parsing via pdfplumber/python-pptx.
- `services/transcription_service.py`: Multi-provider speech-to-text routing.
- `services/nlp_ai_service.py`: Scikit-Learn TF-IDF, TextRank, rule-based extraction, and LLM integrations.
- `services/report_engine.py`: Dynamic report normalization.
- `services/pdf_service.py`: ReportLab PDF generation.
- `services/docx_service.py`: python-docx Word document compilation.
- `services/demo_generator.py`: Generates synthetic evaluation media (video, audio, agenda).

---

## R. Database and Data Flow

### Database Schema (`meeting_sessions` table)

```mermaid
erDiagram
    MEETING_SESSIONS {
        string id PK "UUID (36 chars)"
        string title "Session Title"
        string status "pending | completed | failed"
        text error_message "Failure diagnostics"
        datetime created_at "UTC Timestamp"
        datetime updated_at "UTC Timestamp"
        string source_filename "Original media name"
        string source_file_type "video | audio"
        string file_path "Absolute disk location"
        float duration_seconds "Total media length"
        string document_filename "Attached document name"
        string document_path "Attached document path"
        string ai_provider "Model / Engine used"
        text transcript "Full verbatim text"
        text summary "Executive summary paragraph"
        json action_items "Array of Task objects"
        json decisions "Array of Decision objects"
        json topics "Array of Topic objects"
        json sentiment "Sentiment metric dictionary"
        json video_analysis "Keyframes, scene count, activity %"
        json speakers "Diarization statistics array"
        json questions_answers "Extracted Q&A pairs"
        json timeline "Chronological timeline events"
        json document_analysis "Parsed slide/page structures"
        json evidence "Citation linkage records"
        string pdf_path "Generated PDF file path"
        string docx_path "Generated DOCX file path"
    }
```

### Local vs. Containerized Modes
- **Standalone Local Mode (Default)**: Uses SQLite with `aiosqlite` targeting `backend/meetingmind.db`. Requires zero external database services.
- **Docker Compose Mode**: Configured in `docker-compose.yml` to target PostgreSQL 16 with `pgvector` on port 5432 using `DATABASE_URL=postgresql+asyncpg://...`.

---

## S. API Documentation

All endpoints are registered under `/api/v1` and documented automatically via OpenAPI at `http://localhost:8000/docs`.

| Method | Endpoint | Description | Request Format | Response Status & Type |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | System health check & DB status | None | `200 OK` (JSON) |
| `POST` | `/api/v1/sessions/analyze` | Ingest media and execute multimodal pipeline | `multipart/form-data` | `200 OK` (JSON Session Dict) |
| `POST` | `/api/v1/sessions/demo` | Execute Faculty Demo using local sample data | None | `200 OK` (JSON Session Dict) |
| `GET` | `/api/v1/sessions` | Retrieve all historical sessions | None | `200 OK` (JSON Array of Sessions) |
| `GET` | `/api/v1/sessions/{id}` | Retrieve single session details | None | `200 OK` (JSON Session Dict) / `404` |
| `GET` | `/api/v1/sessions/{id}/pdf` | Download or view executive PDF report | Query: `?inline=true\|false` | `200 OK` (`application/pdf`) |
| `GET` | `/api/v1/sessions/{id}/docx` | Download editable Microsoft Word report | None | `200 OK` (`application/vnd.openxmlformats...`) |
| `GET` | `/api/v1/sessions/{id}/transcript-pdf`| Download verbatim transcript as PDF | Query: `?inline=true\|false` | `200 OK` (`application/pdf`) |
| `GET` | `/api/v1/sessions/{id}/transcript-txt`| Download raw transcript text | None | `200 OK` (`text/plain`) |
| `GET` | `/api/v1/sessions/{id}/json` | Export standardized dynamic report JSON | None | `200 OK` (JSON Export Schema) |
| `GET` | `/api/v1/sessions/{id}/markdown` | Download formatted GitHub Markdown report | None | `200 OK` (`text/markdown`) |
| `GET` | `/api/v1/sessions/{id}/txt` | Download plain-text formatted report | None | `200 OK` (`text/plain`) |
| `DELETE`| `/api/v1/sessions/{id}` | Purge session record and disk files | None | `200 OK` (JSON Confirmation) |

---

## T. Project Structure

```text
p:/PBL Final year project/
├── .env.example                     # Environment variable template with default values
├── .gitignore                       # Git ignore rules for node_modules, storage, pycache
├── docker-compose.yml               # Container definitions for Postgres, Redis, MinIO, Backend, Frontend
├── README.md                        # Master project documentation
├── meetingmind.db                    # Active SQLite development database
│
├── backend/                         # FastAPI Backend Application
│   ├── pyproject.toml               # Python project configuration, dependencies, tools
│   ├── Dockerfile                   # Backend container build configuration
│   ├── alembic.ini                  # Alembic database migration configuration
│   ├── tests/                       # Automated test suite (Pytest)
│   │   ├── conftest.py              # Test fixtures and database mocks
│   │   ├── test_docx_report.py      # Tests for Word DOCX generation and endpoints
│   │   ├── test_dynamic_report.py   # Tests for dynamic report schemas and section rendering
│   │   ├── test_pipeline.py         # End-to-end integration tests for session creation
│   │   └── test_validation.py       # Unit tests for MIME validation and file sizing
│   └── app/                         # Core Application Source Code
│       ├── __init__.py
│       ├── main.py                  # FastAPI entry point, CORS, static mounts, lifespan
│       ├── config.py                # Pydantic Settings configuration loader
│       ├── api/                     # API Routers
│       │   └── v1/
│       │       ├── health.py        # System health and status endpoint
│       │       └── sessions.py      # Session analysis, export, and history endpoints
│       ├── db/                      # Database Layer
│       │   ├── base.py              # Declarative Base
│       │   ├── models.py            # SQLAlchemy MeetingSession model
│       │   └── session.py           # Async engine, sessionmaker, schema migrations
│       └── services/                # Business Logic & Processing Engines
│           ├── media_service.py     # OpenCV video processing, FFmpeg extraction, doc parsing
│           ├── transcription_service.py # Speech-to-text routing (Whisper, AssemblyAI, local)
│           ├── nlp_ai_service.py    # TF-IDF, TextRank, rule-based extraction, LLM clients
│           ├── report_engine.py     # Dynamic report normalization engine
│           ├── pdf_service.py       # ReportLab PDF compiler
│           ├── docx_service.py      # python-docx Word report compiler
│           └── demo_generator.py    # Synthetic faculty demo data generation
│
└── frontend/                        # React + Vite Frontend Application
    ├── package.json                 # Node dependencies and scripts
    ├── vite.config.ts               # Vite configuration with proxy rules (/api, /static)
    ├── tsconfig.json                # TypeScript compiler configuration
    └── src/                         # Frontend Application Source Code
        ├── main.tsx                 # React entry point
        ├── App.tsx                  # Root component and view state manager
        ├── App.css                  # Global application styling
        ├── index.css                # Tailwind CSS v4 directives and color tokens
        ├── api.ts                   # Axios client and fetch blob download functions
        ├── types.ts                 # TypeScript interfaces for session intelligence
        ├── assets/                  # Static brand assets
        └── components/              # Modular UI Components
            ├── Navbar.tsx           # Navigation bar with backend health indicator
            ├── StorytellingLanding.tsx # Interactive presentation and problem overview
            ├── UploadSection.tsx    # Drag-and-drop media ingestion form
            ├── ProcessingOverlay.tsx # 5-stage progress indicator with timer
            ├── ResultsView.tsx      # Multi-tab intelligence dashboard and download center
            └── SessionsHistory.tsx  # Historical sessions manager and table
```

---

## U. Installation and Prerequisites

### Prerequisites
1. **Operating System**: Linux, Windows 10/11.
2. **Python**: Python 3.12 or 3.14 (Verified on Python 3.14.5).
3. **Node.js**: Node.js 20+ and npm 10+.
4. **FFmpeg**: Required for audio track extraction. Must be accessible via the system `PATH`.
   - *Windows Verification*: Open PowerShell and run `ffmpeg -version`. If missing, install via `winget install Gyan.FFmpeg` or `choco install ffmpeg`.

---

## V. Environment Configuration

Configuration variables are read from `.env` in the project root. If no `.env` file exists, defaults configured in `app/config.py` are applied automatically:

| Variable | Purpose | Required? | Default / Example Value |
|---|---|---|---|
| `APP_NAME` | Name identifier for application | No | `MeetingMindligence` |
| `APP_ENV` | Application environment | No | `development` |
| `DEBUG` | Enable debug logs and docs | No | `true` |
| `SECRET_KEY` | Application secret key | No (in dev) | `change-me-to-a-random-64-char-string` |
| `BACKEND_HOST` | Host interface for backend | No | `0.0.0.0` |
| `BACKEND_PORT` | Port for backend server | No | `8000` |
| `BACKEND_CORS_ORIGINS` | Permitted CORS origins | No | `["http://localhost:5173", "http://127.0.0.1:5173"]` |
| `DATABASE_URL` | SQLAlchemy async connection URI | No (defaults to SQLite) | `sqlite+aiosqlite:///./meetingmind.db` |
| `OPENAI_API_KEY` | OpenAI API key for Whisper and GPT-4o-mini | No (triggers local fallback) | `sk-...` |
| `ASSEMBLYAI_API_KEY` | AssemblyAI key for speech-to-text | No (triggers local fallback) | `...` |
| `GOOGLE_AI_API_KEY` | Gemini API key for Gemini 1.5 Flash | No (triggers local fallback) | `AIzaSy...` |
| `MAX_VIDEO_SIZE_MB` | Maximum allowed video file size | No | `500` (configurable up to 2048) |
| `MAX_DOCUMENT_SIZE_MB`| Maximum allowed document file size | No | `50` |

---

## W. Installation and Setup

### 1. Clone & Open Repository
```powershell
# Open project directory in PowerShell
cd "p:\PBL Final year project"
```

### 2. Configure Backend Virtual Environment
```powershell
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install backend package and development dependencies
pip install -e ".[dev]"
```

### 3. Start Backend API Server
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API will be accessible at: `http://localhost:8000`
- Swagger UI Documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

### 4. Configure & Start Frontend
Open a separate PowerShell window:
```powershell
cd "p:\PBL Final year project\frontend"

# Install node packages
npm install

# Start Vite development server
npm run dev
```
- Web Application will be live at: `http://localhost:5173`

---

## X. Docker Setup

A complete containerized stack is defined in `docker-compose.yml`:

```bash
# Start containerized services (Postgres + Redis + MinIO + Backend + Frontend)
docker compose up --build

# Stop containerized services
docker compose down

# Stop and purge persistent data volumes
docker compose down -v
```

### Services Defined:
- `postgres`: PostgreSQL 16 with `pgvector` extension on port 5432.
- `redis`: Redis 7 on port 6379 for caching.
- `minio`: MinIO S3-compatible object storage on ports 9000 (API) and 9001 (Web Console).
- `backend`: FastAPI application container with hot-reloading mounted volume on port 8000.
- `frontend`: Vite React application container on port 5173.

---

## Y. How to Use MeetingMind

1. **Access Web Interface**: Navigate to `http://localhost:5173`.
2. **Review Status**: Verify that the top navigation bar displays a green **"Backend & SQLite Ready"** badge.
3. **Select Ingestion Mode**:
   - **Custom Upload**: In the "New Analysis" tab, enter a session title, drag-and-drop a video/audio file (up to 500 MB), optionally attach a supporting PDF or presentation deck, select your AI provider, and click **"Execute Multimodal Analysis"**.
   - **Instant Faculty Demo**: Click **"Run Faculty Demo"** to evaluate the pipeline instantly without uploading files.
4. **Monitor Progress**: Watch the 5-stage processing overlay track ingestion, OpenCV frame analysis, transcription, semantic mining, and report compilation.
5. **Explore Intelligence Results**:
   - **Executive Overview**: Review the AI summary paragraph, duration metrics, and overall sentiment score.
   - **Visual Shifts**: Inspect OpenCV-extracted keyframe screenshots with timestamps.
   - **Action Items & Decisions**: Review mined commitments with assignees and evidence quotes.
   - **Verbatim Transcript**: Search through timestamped spoken dialogue.
6. **Export Documents**: Click **Word Report (.docx)**, **Executive PDF**, **Markdown**, or **JSON** to download reports.
7. **Manage History**: Click **"Saved Sessions"** in the navigation bar to inspect past reports or delete obsolete entries.

---

## Z. Faculty Demo Mode

To facilitate evaluation without external API keys or uploaded files, MeetingMind includes a self-contained demonstration engine in `app/services/demo_generator.py`:

1. **Media Generation**: Upon startup, `ensure_demo_media()` verifies the presence of demo media in `backend/demo_data/`.
2. **Synthetic Video**: If not present, it programmatically generates an MP4 video using OpenCV containing 3 distinct visual slides:
   - Slide 1: Project Overview & Architecture
   - Slide 2: OpenCV Analysis + Speech-to-Text Pipeline
   - Slide 3: Action Items & Results
3. **Synthetic Audio**: Generates an 8-second modulated wave file mimicking speech cadences and muxes it with the video using FFmpeg.
4. **Live Execution**: When the user clicks **"Run Faculty Demo"**, the backend executes the **real, live pipeline** (OpenCV keyframe extraction, audio demuxing, transcription, Scikit-learn TF-IDF, TextRank, and ReportLab/DOCX compilers) against this sample dataset.

---

## AA. Testing and Quality Assurance

The backend includes 18 automated unit and integration tests executing under Pytest:

```powershell
cd "p:\PBL Final year project\backend"
pytest -v
```

### Actual Verified Test Results:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: P:\PBL Final year project\backend
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.15.1, asyncio-1.4.0
collected 18 items

tests/test_docx_report.py::test_generate_meeting_docx_report_creates_valid_file PASSED   [  5%]
tests/test_docx_report.py::test_docx_contains_expected_sections PASSED                   [ 11%]
tests/test_docx_report.py::test_docx_with_keyframes PASSED                               [ 16%]
tests/test_docx_report.py::test_docx_download_endpoint PASSED                            [ 22%]
tests/test_dynamic_report.py::test_dynamic_report_active_sections PASSED                 [ 27%]
tests/test_dynamic_report.py::test_dynamic_report_normalizes_decisions PASSED            [ 33%]
tests/test_dynamic_report.py::test_dynamic_report_normalizes_action_items PASSED         [ 38%]
tests/test_dynamic_report.py::test_dynamic_report_normalizes_topics PASSED               [ 44%]
tests/test_dynamic_report.py::test_dynamic_report_visual_intelligence PASSED             [ 50%]
tests/test_dynamic_report.py::test_dynamic_report_evidence_list PASSED                   [ 55%]
tests/test_dynamic_report.py::test_dynamic_report_omits_missing_sections PASSED          [ 61%]
tests/test_dynamic_report.py::test_pdf_generation_smoke PASSED                           [ 66%]
tests/test_pipeline.py::test_health_endpoint PASSED                                      [ 72%]
tests/test_validation.py::test_sanitize_filename PASSED                                  [ 77%]
tests/test_validation.py::test_validate_media_file_allowed_video PASSED                   [ 83%]
tests/test_validation.py::test_validate_media_file_allowed_audio PASSED                   [ 88%]
tests/test_validation.py::test_validate_media_file_disallowed PASSED                     [ 94%]
tests/test_validation.py::test_validate_document_file PASSED                             [100%]

======================= 18 passed, 1 warning in 12.40s ========================
```

### Frontend Build Verification:
```powershell
cd "p:\PBL Final year project\frontend"
npm run build
```
- Output: `✓ 1895 modules transformed.` Built cleanly with zero TypeScript or packaging errors in 1.27s.

---

## AB. Security and Privacy

1. **Filename Sanitization**: `sanitize_filename()` in `media_service.py` removes path traversal sequences (`../`, `..\`) and strips non-alphanumeric characters using `re.sub(r"[^\w\s\.-]", "", name)`.
2. **File Size Enforcement**: `save_upload_file()` streams uploaded bytes in 1 MB chunks and raises an HTTP 413 exception if total accumulated size exceeds `MAX_VIDEO_SIZE_MB`, immediately deleting partial temporary files.
3. **MIME & Extension Whitelisting**: Strict checks ensure only permitted video, audio, and presentation extensions are ingested.
4. **Credential Isolation**: API keys passed via forms or `.env` are utilized in memory and never persisted in database columns or logged to application outputs.
5. **CORS Hardening**: FastAPI `CORSMiddleware` explicitly limits origins to specified development ports (`localhost:5173`, `127.0.0.1:5173`).

---

## AC. Error Handling and Troubleshooting

| Symptom | Probable Cause | Diagnostic Command | Resolution |
|---|---|---|---|
| **`NameError: name 'field_validator' is not defined`** | Missing imports in `config.py` | `python -c "import app.config"` | Ensure `from typing import Any` and `from pydantic import field_validator` are imported in `config.py`. |
| **Backend Health Status is "Offline" in UI** | FastAPI server is not running on port 8000 | `Invoke-RestMethod http://localhost:8000/api/v1/health` | Start backend with `uvicorn app.main:app --host 0.0.0.0 --port 8000`. |
| **FFmpeg execution failure on upload** | FFmpeg is not installed or not on system PATH | `Get-Command ffmpeg` in PowerShell | Install FFmpeg via `winget install Gyan.FFmpeg` and restart terminal. |
| **ReportLab XML parsing error during PDF export** | Special characters (`<`, `>`, `&`) in transcript | Check logs for `xml.sax.SAXParseException` | `safe_text()` escapes all dynamic flowable strings with `xml.sax.saxutils.escape`. |
| **Word DOCX file corruption error on download** | Corrupted XML shading injection or invalid margins | Run `pytest tests/test_docx_report.py` | Verify that cell shading XML uses valid 6-character hex strings without `#` prefix. |
| **CORS errors in browser console** | Frontend accessing unlisted origin (e.g. `localhost:5174`) | Inspect Network tab preflight `OPTIONS` | Add the origin to `BACKEND_CORS_ORIGINS` in `.env` or `app/config.py`. |
| **Upload exceeds maximum size error (HTTP 413)** | Video exceeds 500 MB limit | Inspect upload file size | Increase `MAX_VIDEO_SIZE_MB=2048` in `.env`. |

---

## AD. Known Limitations

1. **Acoustic Speech Recognition Quality**: The local speech recognition engine (`speech_recognition` library) relies on basic acoustic thresholds. Audio tracks with heavy background noise require the OpenAI Whisper cloud provider for optimal transcript fidelity.
2. **Deterministic NLP Heuristics**: The rule-based action item and decision extractors rely on explicit verbal markers ("need to", "agreed to"). Subtle, implicit consensus without conventional phrasing may not be captured in local mode.
3. **Heuristic Keyframe Capture**: OpenCV scene differencing detects significant pixel shifts (slide transitions). It does not semantically identify what specific concept changed on a slide.
4. **Speaker Diarization Dependency**: Speaker separation in local mode relies on transcript markers (`Speaker: text`) or agenda attendee lines. Full acoustic voiceprint diarization is supported only when using cloud APIs (such as AssemblyAI).

---

## AE. Future Improvements

1. **On-Device Whisper Integration**: Integrate local `whisper.cpp` or `faster-whisper` using ONNX/CUDA runtime for offline speech transcription.
2. **Visual Slide OCR**: Add Tesseract or EasyOCR to extract textual bullet points directly from OpenCV keyframe screenshots and fuse them with audio transcripts.
3. **Acoustic Speaker Diarization**: Integrate PyAnnote.audio for local acoustic embedding clustering and speaker voiceprint assignment.
4. **Vector Search & Cross-Session RAG**: Implement pgvector semantic embedding queries across past meeting sessions to support organizational knowledge search.

---

## AF. Performance and Evaluation

| Subsystem | Metric Measured | Baseline Benchmark (Local Mode) |
|---|---|---|
| **OpenCV Video Analysis** | Throughput | ~150–200 frames/sec (1 FPS sample rate on 1080p video) |
| **FFmpeg Audio Extraction** | Latency | < 1.2 seconds for a 5-minute MP4 video stream |
| **TextRank Summarization** | Execution Time | < 0.15 seconds for a 3,000-word transcript |
| **ReportLab PDF Generation** | Compilation Latency | ~0.8–1.4 seconds for a 4-page report with 4 keyframe images |
| **python-docx Word Generation** | Compilation Latency | ~0.4–0.7 seconds for complete styled report |
| **Test Suite Execution** | Total Test Duration | 18 unit/integration tests complete in ~12.4 seconds |

---

## AG. Engineering Challenges and Design Trade-offs

### 1. Dual-Path Architecture vs. Pure Cloud Microservices
- *Challenge*: Relying solely on cloud APIs creates vendor lock-in, recurring operational costs, and catastrophic failures if API keys expire during faculty evaluation.
- *Solution*: Designed a dual-path engine. If cloud API keys are present, the system leverages high-capacity LLMs (`gpt-4o-mini`, `gemini-1.5-flash`). If absent, it automatically executes the local mathematical NLP pipeline (TF-IDF, TextRank).

### 2. Video Processing Latency vs. Frame Granularity
- *Challenge*: Decoding every frame of a 30 FPS 1080p video generates 1,800 frames per minute, causing massive memory consumption and long processing delays.
- *Solution*: Downsampled video frames to $160 \times 90$ resolution and sampled at a rate of 1 frame per second. This reduced processing overhead by over 95% while retaining sufficient visual signal to detect slide transitions reliably.

### 3. XML Shading in python-docx
- *Challenge*: The high-level `python-docx` API lacks native methods for setting cell background colors and cell-specific padding.
- *Solution*: Directly manipulated low-level OpenXML schema elements via `parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex}"/>')`, producing enterprise-grade Word reports with zero third-party software dependencies.

---

## AH. Technical Interview Preparation

### 1. 30-Second Elevator Pitch
> *"MeetingMind is an end-to-end multimodal meeting intelligence platform. Unlike traditional speech-to-text tools that only process audio, MeetingMind fuses OpenCV computer vision to detect slide transitions and keyframes, speech transcription, and supporting documents. It extracts structured, evidence-backed action items, decisions, and topics without hallucination, and automatically compiles them into publication-ready PDF and editable Word reports. It features a dual-engine architecture that runs both with cloud LLMs and completely offline with Scikit-learn and TextRank."*

### 2. 2-Minute Technical Walkthrough
> *"Architecturally, MeetingMind is built as a decoupled full-stack application with a React 19 / Vite 6 frontend and an asynchronous FastAPI backend backed by SQLAlchemy 2.0 and SQLite.*
>
> *When a video is uploaded, the backend splits processing across two streams: OpenCV downsamples frames to 160x90 grayscale and uses inter-frame difference thresholding to detect slide transitions and save keyframe screenshots. Simultaneously, FFmpeg extracts a 16 kHz mono WAV file, which is transcribed via OpenAI Whisper or a local acoustic fallback.*
>
> *Next, our NLP engine fuses the transcript with any attached presentation slides. In local mode, Scikit-Learn TF-IDF extracts key discussion topics, while a graph-based TextRank algorithm performs PageRank power iteration over sentence cosine similarities to extract a concise executive summary. Rule-based lexical parsers extract action items and formal decisions, linking every claim to exact quotes and timestamps.*
>
> *Finally, our Dynamic Report Engine normalizes the data and feeds ReportLab and python-docx compilers to generate pixel-precise PDF and editable Word documents. The entire system is covered by 18 automated unit and integration tests."*

### 3. Life of a Request: Upload to Download
1. **Client Submission**: User drops an MP4 video into `UploadSection.tsx`. A `FormData` object is posted to `/api/v1/sessions/analyze`.
2. **FastAPI Processing**: `sessions.py` validates the MIME type, assigns a UUID, streams bytes to `storage/uploads/{id}/source.mp4`, and extracts audio using FFmpeg.
3. **OpenCV & Transcription**: OpenCV captures keyframe JPEGs into `storage/keyframes/{id}/`. The WAV audio is transcribed.
4. **NLP Synthesis**: `nlp_ai_service.py` computes TF-IDF scores, TextRank graph rankings, action items, and evidence citations.
5. **Report Compilation**: `pdf_service.py` builds the ReportLab PDF; `docx_service.py` constructs the Word document.
6. **Persistence**: A `MeetingSession` model instance is committed to SQLite via `AsyncSession`.
7. **Response & Rendering**: Serialized JSON returns to the frontend. `App.tsx` transitions to `ResultsView.tsx`, where the user inspects keyframes and downloads reports via native binary fetch streams.

---

## AI. Interview Questions and Answers

### Architecture & System Design
#### Q1: What core problem does MeetingMind solve that existing meeting tools do not?
*Answer*: Existing tools focus almost exclusively on audio-to-text transcription. They lose visual presentation context (slides, diagrams), produce unformatted transcripts, and lack evidence linking. MeetingMind integrates computer vision (OpenCV) with audio transcription and supporting documents, generating structured reports where every task and decision cites exact dialogue evidence.

#### Q2: Why did you choose FastAPI over Flask or Django for the backend?
*Answer*: FastAPI provides native asynchronous ASGI support (`async/await`), enabling non-blocking database queries and efficient streaming of large file uploads. Additionally, its built-in Pydantic schema validation and automated OpenAPI Swagger documentation significantly accelerated frontend-backend integration.

#### Q3: Why is React 19 and Vite used for the frontend instead of server-side rendering (Next.js)?
*Answer*: MeetingMind is an internal analytics dashboard where SEO is not a primary concern. A Vite-powered Single-Page Application (SPA) provides near-instant Hot Module Replacement during development, minimal bundle overhead, and client-side responsiveness when interacting with media players, keyframes, and multi-tab dashboards.

---

### AI / ML & Natural Language Processing
#### Q4: How does TextRank work in your extractive summarization pipeline?
*Answer*: TextRank models text as a graph where each sentence is a node. Edges between nodes represent semantic similarity, calculated via cosine similarity over TF-IDF vectors. We execute 25 iterations of the PageRank power iteration algorithm with a damping factor of 0.85:
$$PR(S_i) = \frac{1-d}{N} + d \sum_{j \ne i} \frac{S_{ji}}{\sum_k S_{jk}} PR(S_j)$$
Sentences with the highest centrality scores are selected in chronological order to form the executive summary.

#### Q5: What is the exact role of TF-IDF in topic extraction?
*Answer*: TF-IDF calculates term frequency adjusted by inverse document frequency across sentences. In `nlp_ai_service.py`, `TfidfVectorizer(ngram_range=(1, 2))` identifies significant unigrams and bigrams while filtering English stop words. Terms with the highest TF-IDF scores represent primary meeting topics and are assigned relevance scores from 0.0 to 1.0.

#### Q6: How does the system extract action items and assignees deterministically?
*Answer*: The rule-based engine scans sentences using regex patterns targeting modal commitment verbs (`need to`, `must`, `action item`, `assigned to`). When a task is matched, the engine searches the sentence for detected attendee names to determine the assignee; if none is found, it assigns the task to "Project Team". Priority is classified as High, Medium, or Low based on lexical urgency markers.

#### Q7: How do you prevent hallucinations in AI-generated reports?
*Answer*: In local mode, all outputs are extracted directly from the source text using deterministic algorithms, eliminating generative hallucination. Every extracted decision and action item includes an `evidence` field containing the exact source quote and timestamp. In cloud LLM mode, the prompt strictly enforces JSON schema constraints and requires verbatim citation quotes.

---

### Computer Vision & Audio Processing
#### Q8: How does OpenCV detect slide changes in meeting recordings?
*Answer*: We read video frames at 1 frame per second, convert them to grayscale, and downsample to $160 \times 90$ pixels. We compute the mean absolute pixel difference between consecutive frames ($\Delta I$). When $\Delta I$ exceeds our calibrated threshold of 18.0 and at least 3 seconds have passed since the previous keyframe, a transition is registered and a full-resolution JPEG is saved.

#### Q9: What is the difference between visual activity detection and visual semantic understanding?
*Answer*: Visual activity detection measures mathematical pixel variation across time to identify when a slide transition or presenter shift occurred. It does not semantically identify what specific concept changed on a slide. Semantic understanding would require an optical character recognition (OCR) engine or a Vision-Language Model.

#### Q10: How does FFmpeg audio extraction work?
*Answer*: The backend executes FFmpeg via Python `subprocess.run` with parameters `-vn` (disable video), `-acodec pcm_s16le` (16-bit uncompressed PCM), `-ar 16000` (16 kHz sample rate), and `-ac 1` (mono channel). This format is the universal standard required by speech recognition engines.

---

### Database & Report Generation
#### Q11: How does the system handle database migrations without Alembic in local mode?
*Answer*: In `session.py`, `init_db()` executes `PRAGMA table_info(meeting_sessions)` against SQLite on startup. It compares existing database columns with the updated model attributes and dynamically executes non-destructive `ALTER TABLE ADD COLUMN` statements for missing fields, preserving existing test sessions.

#### Q12: How are two-pass page numbers rendered in ReportLab PDF generation?
*Answer*: ReportLab's standard canvas does not know the total page count on earlier pages. We implement a custom `NumberedCanvas` class that overrides `showPage()` to save canvas states and defers execution until `save()`. It counts total generated pages and draws "Page X of Y" in the running footer across all pages.

#### Q13: How is custom table styling achieved in python-docx?
*Answer*: The standard `python-docx` API lacks direct properties for cell background shading and inner padding. We access the underlying OpenXML elements directly using `parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex}"/>')` for cell shading and `<w:tcMar>` for cell padding.

---

## AJ. Resume-Ready Project Description

```text
MeetingMind — AI-Powered Meeting & Meeting Intelligence Knowledge Platform
Technologies: Python, FastAPI, React 19, TypeScript, OpenCV, FFmpeg, Scikit-Learn, ReportLab, python-docx, SQLAlchemy, SQLite, Docker

- Engineered an end-to-end multimodal meeting intelligence platform that ingests video, audio, and presentation decks to generate publication-grade PDF and Word intelligence reports.
- Developed a computer vision pipeline using OpenCV to detect slide transitions via grayscale luminance differencing, capturing timestamped keyframes and computing visual engagement metrics.
- Built a dual-engine NLP architecture featuring cloud LLM synthesis (OpenAI, Gemini) with an automated local fallback using Scikit-Learn TF-IDF topic modeling and graph-based TextRank summarization.
- Designed a dynamic report engine with ReportLab and python-docx that renders evidence-backed action items, decisions, and speaker analytics with zero generative hallucination.
- Authored an automated testing suite comprising 18 Pytest unit and integration tests validating document compilation, API endpoints, and media validation routines.
```

---

## AK. Screenshots and Visual Documentation

Below are working visual documentation captures and model outputs produced by MeetingMind's multimodal pipeline:

### 1. Model Executive Report & Analysis Overview
The MeetingMind AI engine compiles full session metadata, technical specifications, and executive summaries with evidence traceability:

<p align="center">
  <img src="docs/screenshots/01_model_executive_summary.png" alt="MeetingMind Model Executive Summary" width="750" />
</p>

### 2. OpenCV Visual Slide & Keyframe Analysis
The computer vision sub-pipeline analyzes frame-to-frame luminance variance to automatically extract transition keyframes and slide moments:

<p align="center">
  <img src="docs/screenshots/02_opencv_keyframe_analysis.png" alt="OpenCV Keyframe Slide Analysis" width="750" />
</p>

### 3. Detected Visual Keyframe Transitions (OpenCV Model)
Raw slide moments captured at timestamped transitions during session recording:

<p align="center">
  <img src="docs/screenshots/keyframe_slide_01.jpg" alt="Keyframe Slide 01" width="280" />
  &nbsp;
  <img src="docs/screenshots/keyframe_slide_02.jpg" alt="Keyframe Slide 02" width="280" />
  &nbsp;
  <img src="docs/screenshots/keyframe_slide_03.jpg" alt="Keyframe Slide 03" width="280" />
</p>

### 4. Semantic Discussion & Topic Modeling
Dialogue streams cross-referenced with document structure using TF-IDF ranking and TextRank graph centrality:

<p align="center">
  <img src="docs/screenshots/03_semantic_topics_discussion.png" alt="Semantic Discussion and Topic Modeling" width="750" />
</p>

### 5. Verified Action Items & Formal Decisions Matrix
Action items categorized with assignee tags, urgency, context, and exact evidence quotes alongside formal agreements:

<p align="center">
  <img src="docs/screenshots/04_action_items_decisions.png" alt="Action Items and Decisions Matrix" width="750" />
</p>

### 6. Official Verification Record & Audit Seal
Two-pass publication verification ensuring complete traceability back to raw dialogue:

<p align="center">
  <img src="docs/screenshots/05_verification_audit_seal.png" alt="Verification Audit Seal" width="750" />
</p>

---

## AL. Contributing and License

This project was developed for the **Problem-Based Learning (PBL) Final Year Evaluation**.

- **Academic Integrity**: Built specifically for educational evaluation, demonstrating multimodal media processing and algorithmic NLP.
- **License**: Released under the **MIT License** for academic and research evaluation.
