import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Sparkles,
  PlayCircle,
  Upload,
  Video,
  FileText,
  ArrowDown,
  BrainCircuit,
  Eye,
  Mic,
  ArrowRight,
  Check,
  AlertCircle,
  X,
  FileCheck,
} from 'lucide-react';

/* ───────────────────────────────────────────────────────────
   TYPES & CONSTANTS
   ─────────────────────────────────────────────────────────── */

interface StorytellingLandingProps {
  onSubmit: (formData: FormData) => void;
  onRunDemo: () => void;
  isProcessing: boolean;
}

const STORY_STAGES = [
  { id: 'stage-hero',         number: '01', short: 'Intro' },
  { id: 'stage-problem',      number: '02', short: 'Problem' },
  { id: 'stage-input',        number: '03', short: 'Input' },
  { id: 'stage-ai',           number: '04', short: 'AI Core' },
  { id: 'stage-intelligence', number: '05', short: 'Insights' },
  { id: 'stage-report',       number: '06', short: 'Report' },
  { id: 'stage-try',          number: '07', short: 'Analyze' },
] as const;

/* ───────────────────────────────────────────────────────────
   useIntersectionReveal — lightweight reveal hook
   ─────────────────────────────────────────────────────────── */
function useIntersectionReveal() {
  const refs = useRef<Map<string, HTMLElement>>(new Map());

  const setRef = useCallback((id: string) => (el: HTMLElement | null) => {
    if (el) refs.current.set(id, el);
    else refs.current.delete(id);
  }, []);

  useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      // Immediately reveal everything
      refs.current.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' },
    );

    refs.current.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return setRef;
}

/* ───────────────────────────────────────────────────────────
   COMPONENT
   ─────────────────────────────────────────────────────────── */
export const StorytellingLanding: React.FC<StorytellingLandingProps> = ({
  onSubmit,
  onRunDemo,
  isProcessing,
}) => {
  /* ── Scroll tracking ── */
  const [activeStageIndex, setActiveStageIndex] = useState(0);
  const [scrollProgress, setScrollProgress] = useState(0);

  /* ── Form state ── */
  const [title, setTitle] = useState('Executive Architecture & Planning Sync');
  const [mediaFile, setMediaFile] = useState<File | null>(null);
  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [provider, setProvider] = useState<'auto' | 'local_ml' | 'openai' | 'gemini'>('auto');
  const [apiKey, setApiKey] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isDraggingMedia, setIsDraggingMedia] = useState(false);

  const mediaInputRef = useRef<HTMLInputElement>(null);
  const docInputRef = useRef<HTMLInputElement>(null);

  const allowedMediaExts = ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.m4a', '.ogg', '.flac'];
  const allowedDocExts = ['.pdf', '.pptx', '.ppt', '.txt', '.docx'];

  /* ── Reveal hook ── */
  const setRevealRef = useIntersectionReveal();

  /* ── Scroll spy & progress ── */
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? Math.min(1, Math.max(0, scrollY / docHeight)) : 0;
      setScrollProgress(progress);

      const midPoint = window.innerHeight * 0.45;
      for (let i = STORY_STAGES.length - 1; i >= 0; i--) {
        const el = document.getElementById(STORY_STAGES[i].id);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= midPoint) {
            setActiveStageIndex(i);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  /* ── Helpers ── */
  const scrollToStage = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  const validateFile = (file: File, allowedExts: string[], maxMb: number): string | null => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedExts.includes(ext)) return `Invalid format '${ext}'. Allowed: ${allowedExts.join(', ')}`;
    if (file.size / (1024 * 1024) > maxMb) return `File exceeds ${maxMb}MB limit.`;
    return null;
  };

  const handleMediaSelect = (file: File) => {
    const err = validateFile(file, allowedMediaExts, 500);
    if (err) { setErrorMsg(err); return; }
    setErrorMsg(null);
    setMediaFile(file);
  };

  const handleDocSelect = (file: File) => {
    const err = validateFile(file, allowedDocExts, 50);
    if (err) { setErrorMsg(err); return; }
    setErrorMsg(null);
    setDocumentFile(file);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!mediaFile) {
      setErrorMsg('Please select a video or audio file to analyze.');
      scrollToStage('stage-try');
      return;
    }
    setErrorMsg(null);
    const formData = new FormData();
    formData.append('title', title.trim() || 'Meeting Intelligence Session');
    formData.append('file', mediaFile);
    if (documentFile) formData.append('document', documentFile);
    if (provider !== 'auto') formData.append('provider', provider);
    if (apiKey.trim()) formData.append('api_key', apiKey.trim());
    onSubmit(formData);
  };

  /* ═══════════════════════════════════════════════════════════
     RENDER
     ═══════════════════════════════════════════════════════════ */
  return (
    <div className="relative bg-slate-950 text-slate-100 overflow-x-hidden selection:bg-blue-600 selection:text-white">

      {/* ── Background ambient glow ── */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[900px] h-[550px] bg-gradient-to-b from-blue-600/15 via-indigo-600/10 to-transparent blur-3xl opacity-70" />
        <div className="absolute top-1/3 -left-48 w-[600px] h-[600px] bg-cyan-600/10 blur-3xl rounded-full" />
        <div className="absolute top-2/3 -right-48 w-[600px] h-[600px] bg-indigo-600/10 blur-3xl rounded-full" />
      </div>

      {/* ── Floating progress pill (desktop) ── */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 hidden md:flex items-center space-x-1 px-4 py-2 rounded-full bg-slate-900/90 border border-slate-800/90 shadow-2xl backdrop-blur-md">
        <span className="text-[11px] font-mono font-bold text-slate-400 mr-2 border-r border-slate-800 pr-2.5">
          {STORY_STAGES[activeStageIndex].number} / 07
        </span>
        {STORY_STAGES.map((stage, idx) => (
          <button
            key={stage.id}
            onClick={() => scrollToStage(stage.id)}
            className={`px-2.5 py-1 rounded-full text-[11px] font-semibold transition-all cursor-pointer ${
              idx === activeStageIndex
                ? 'bg-blue-600 text-white shadow-sm'
                : idx < activeStageIndex
                ? 'text-blue-400/70 hover:text-blue-300 hover:bg-slate-800/60'
                : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/60'
            }`}
          >
            {stage.short}
          </button>
        ))}
      </div>

      {/* ── Top reading progress bar ── */}
      <div
        className="fixed top-16 left-0 h-0.5 bg-gradient-to-r from-blue-500 via-indigo-400 to-amber-400 z-50 transition-all duration-150"
        style={{ width: `${scrollProgress * 100}%` }}
      />

      {/* ═════════════════════════════════════════════════════════
          SECTION 1 — HERO
          ═════════════════════════════════════════════════════════ */}
      <section
        id="stage-hero"
        ref={setRevealRef('hero')}
        className="story-section relative z-10 min-h-[92vh] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 pt-12 pb-20 text-center"
      >
        {/* Badge */}
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/25 text-blue-400 text-xs font-semibold mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Multimodal Meeting Intelligence Engine</span>
        </div>

        {/* Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl leading-[1.1]">
          Turn meetings into{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-300 to-indigo-400 shimmer-text">
            actionable intelligence.
          </span>
        </h1>

        <p className="mt-5 text-base sm:text-lg text-slate-300 max-w-2xl leading-relaxed reveal-child">
          Transform raw video, audio, and supporting documents into structured insights,
          verified decisions, prioritized action items, and publication-ready intelligence reports.
        </p>

        {/* Primary CTAs */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3 reveal-child">
          <button
            onClick={() => scrollToStage('stage-try')}
            className="px-6 py-3 rounded-xl text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/25 transition-all flex items-center space-x-2 cursor-pointer group"
          >
            <span>Start Analysis</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>

          <button
            onClick={onRunDemo}
            disabled={isProcessing}
            className="px-6 py-3 rounded-xl text-sm font-semibold bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg shadow-amber-500/20 transition-all flex items-center space-x-2 cursor-pointer disabled:opacity-50"
          >
            <PlayCircle className="w-4 h-4" />
            <span>Run Faculty Demo</span>
          </button>
        </div>

        {/* ── Central Hero Visual: Meeting Viewport ── */}
        <div className="mt-14 relative w-full max-w-3xl scale-reveal">
          <div className="pulse-ring relative aspect-video rounded-2xl bg-slate-900/90 border border-slate-800 shadow-2xl overflow-hidden p-1">
            <div className="w-full h-full rounded-xl bg-slate-950 flex flex-col justify-between p-6 border border-slate-800/80 relative">
              {/* Window chrome */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  <span className="text-xs font-mono text-slate-400 ml-2">Executive Technical Review Sync</span>
                </div>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping mr-1" />
                  01:32 / 08:45
                </span>
              </div>

              {/* Participant cards */}
              <div className="grid grid-cols-3 gap-3 my-4">
                {[
                  { initials: 'AR', name: 'Alex Rivera', role: 'Lead Architect', color: 'blue' },
                  { initials: 'PS', name: 'Priya Sharma', role: 'ML Engineer', color: 'emerald' },
                  { initials: 'DC', name: 'David Chen', role: 'Fullstack Lead', color: 'purple' },
                ].map((p) => (
                  <div key={p.initials} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 text-left">
                    <div className={`w-8 h-8 rounded-lg bg-${p.color}-500/20 flex items-center justify-center text-${p.color}-400 font-bold text-xs mb-2`}>
                      {p.initials}
                    </div>
                    <p className="text-xs font-semibold text-slate-200">{p.name}</p>
                    <p className="text-[10px] text-slate-400">{p.role}</p>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
                <span>Active Audio: 16kHz mono</span>
                <span>OpenCV: Slide change detected</span>
                <span className="hidden sm:inline">Status: Processing</span>
              </div>
            </div>
          </div>

          {/* Floating info fragments */}
          <div className="hidden sm:block absolute -top-4 -left-6 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-blue-500/30 text-blue-300 text-xs shadow-xl float-drift">
            💬 Transcript: &quot;We agreed SQLite is persistent...&quot;
          </div>
          <div className="hidden sm:block absolute -top-4 -right-6 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-emerald-500/30 text-emerald-300 text-xs shadow-xl float-drift-delayed">
            ✓ Decision: &quot;Adopt offline local ML&quot;
          </div>
          <div className="hidden sm:block absolute -bottom-4 -left-8 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-indigo-500/30 text-indigo-300 text-xs shadow-xl float-drift-slow">
            📋 Task: &quot;Prepare benchmark by Friday&quot;
          </div>
          <div className="hidden sm:block absolute -bottom-4 -right-8 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-purple-500/30 text-purple-300 text-xs shadow-xl float-drift">
            🖼️ OpenCV: &quot;Slide 2 Shift at 00:03&quot;
          </div>
        </div>

        {/* Scroll hint */}
        <div className="mt-14 flex flex-col items-center space-y-1.5 text-xs text-slate-500 reveal-child">
          <span>Scroll to discover how VideoIntel works</span>
          <ArrowDown className="w-4 h-4 animate-bounce text-slate-400" />
        </div>
      </section>

      {/* ═════════════════════════════════════════════════════════
          SECTION 2 — THE PROBLEM
          ═════════════════════════════════════════════════════════ */}
      <section
        id="stage-problem"
        ref={setRevealRef('problem')}
        className="story-section relative z-10 min-h-[85vh] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 py-20"
      >
        <div className="max-w-4xl mx-auto text-center">
          <span className="text-[11px] font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/25">
            01 • The Problem
          </span>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white mt-4 tracking-tight">
            Important information gets buried.
          </h2>
          <p className="mt-3 text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Hours of conversations contain decisions, tasks, questions, and context
            that are difficult to track manually.
          </p>
        </div>

        {/* Scattered moments visual */}
        <div className="mt-12 w-full max-w-4xl scale-reveal">
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 shadow-2xl relative overflow-hidden">
            <p className="text-xs font-mono font-bold text-slate-400 mb-4 uppercase tracking-wider">
              Scattered Session Moments
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {[
                { time: '00:14', type: 'Discussion', label: 'Architecture Specs', border: 'border-blue-500/30', text: 'text-blue-400' },
                { time: '01:32', type: 'Decision', label: 'Persistent Storage', border: 'border-emerald-500/30', text: 'text-emerald-400' },
                { time: '02:47', type: 'Question', label: 'Offline Fallback API', border: 'border-cyan-500/30', text: 'text-cyan-400' },
                { time: '04:12', type: 'Task', label: 'Priya: Benchmark Eval', border: 'border-indigo-500/30', text: 'text-indigo-400' },
                { time: '05:21', type: 'Slide', label: 'OpenCV Visual Shift', border: 'border-purple-500/30', text: 'text-purple-400' },
                { time: '06:08', type: 'Follow-up', label: 'Final Faculty Presentation', border: 'border-amber-500/30', text: 'text-amber-400' },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className={`reveal-child p-3.5 rounded-xl bg-slate-950/80 border ${item.border} ${item.text} flex items-center justify-between text-xs`}
                >
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-[11px] text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded">
                      {item.time}
                    </span>
                    <span className="font-semibold text-slate-200">{item.label}</span>
                  </div>
                  <span className="text-[10px] uppercase font-bold text-slate-400">
                    {item.type}
                  </span>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2">
              <span>⚠️ Manual meeting notes miss up to 60% of technical action items and visual context.</span>
              <span className="text-blue-400 font-semibold">So we built VideoIntel →</span>
            </div>
          </div>
        </div>
      </section>

      {/* ═════════════════════════════════════════════════════════
          SECTION 3 — MULTIMODAL INPUT
          ═════════════════════════════════════════════════════════ */}
      <section
        id="stage-input"
        ref={setRevealRef('input')}
        className="story-section relative z-10 min-h-[85vh] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 py-20"
      >
        <div className="max-w-4xl mx-auto text-center">
          <span className="text-[11px] font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/25">
            02 • Multimodal Ingestion
          </span>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white mt-4 tracking-tight">
            One session. Multiple sources.
          </h2>
          <p className="mt-3 text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
            VideoIntel combines what was said, what was shown, and what was provided.
          </p>
        </div>

        {/* Three stream cards */}
        <div className="mt-12 w-full max-w-4xl grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              icon: <Video className="w-5 h-5" />,
              iconBg: 'bg-blue-500/15', iconColor: 'text-blue-400',
              title: '🎥 Video Recording',
              desc: 'OpenCV analyzes slide transitions, presentation screen activity, and visual scene shifts.',
              formats: '.mp4 • .webm • .mkv • .mov',
              formatColor: 'text-blue-400',
              hoverBorder: 'hover:border-blue-500/40',
            },
            {
              icon: <Mic className="w-5 h-5" />,
              iconBg: 'bg-cyan-500/15', iconColor: 'text-cyan-400',
              title: '🔊 Speech & Audio',
              desc: 'Speech-to-text converts multi-speaker dialogue into verbatim transcription with timestamp markers.',
              formats: '.wav • .mp3 • .m4a • Whisper',
              formatColor: 'text-cyan-400',
              hoverBorder: 'hover:border-cyan-500/40',
            },
            {
              icon: <FileText className="w-5 h-5" />,
              iconBg: 'bg-purple-500/15', iconColor: 'text-purple-400',
              title: '📄 Documents & Slides',
              desc: 'Extracts text from meeting slide decks, formal agendas, and specification files to enrich context.',
              formats: '.pdf • .pptx • .docx • .txt',
              formatColor: 'text-purple-400',
              hoverBorder: 'hover:border-purple-500/40',
            },
          ].map((card, idx) => (
            <div
              key={idx}
              className={`reveal-child p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl flex flex-col justify-between ${card.hoverBorder} transition-colors`}
            >
              <div>
                <div className={`w-10 h-10 rounded-xl ${card.iconBg} flex items-center justify-center ${card.iconColor} mb-4`}>
                  {card.icon}
                </div>
                <h3 className="text-base font-bold text-white">{card.title}</h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">{card.desc}</p>
              </div>
              <div className={`mt-4 pt-3 border-t border-slate-800 text-[11px] font-mono ${card.formatColor}`}>
                {card.formats}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 flex items-center space-x-2 text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-4 py-2 rounded-full border border-indigo-500/20 reveal-child">
          <span>Converges into:</span>
          <span className="text-white">UNDERSTAND PIPELINE</span>
        </div>
      </section>

      {/* ═════════════════════════════════════════════════════════
          SECTION 4 — AI INTELLIGENCE ENGINE
          ═════════════════════════════════════════════════════════ */}
      <section
        id="stage-ai"
        ref={setRevealRef('ai')}
        className="story-section relative z-10 min-h-[90vh] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 py-20"
      >
        <div className="max-w-4xl mx-auto text-center">
          <span className="text-[11px] font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/25">
            03 • AI Intelligence Engine
          </span>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white mt-4 tracking-tight">
            VideoIntel doesn&apos;t just transcribe the meeting.
          </h2>
          <p className="mt-3 text-lg text-indigo-300 font-semibold">
            It understands the context.
          </p>
        </div>

        {/* Engine visual */}
        <div className="mt-12 w-full max-w-4xl p-6 sm:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-2xl relative scale-reveal">
          <div className="text-center mb-6">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/15 text-blue-300 text-xs font-mono font-bold">
              <BrainCircuit className="w-4 h-4 text-cyan-400" />
              <span>MULTIMODAL AI INTELLIGENCE CORE</span>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center mb-6">
            {[
              { label: 'SPEECH', detail: 'Whisper & Acoustic STT', color: 'text-blue-400' },
              { label: 'VISION', detail: 'OpenCV Keyframes', color: 'text-cyan-400' },
              { label: 'NLP', detail: 'TextRank & TF-IDF', color: 'text-indigo-400' },
              { label: 'DOCS', detail: 'Slide Alignment', color: 'text-purple-400' },
            ].map((engine, idx) => (
              <div key={idx} className="reveal-child p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className={`text-[10px] font-bold uppercase ${engine.color}`}>{engine.label}</span>
                <p className="text-xs font-semibold text-slate-200 mt-1">{engine.detail}</p>
              </div>
            ))}
          </div>

          {/* Formula banner */}
          <div className="p-4 rounded-xl bg-slate-950 border border-blue-500/30 text-center reveal-child">
            <p className="text-xs sm:text-sm font-mono font-semibold text-slate-200">
              TRANSCRIPT <span className="text-blue-400">+</span> VISUAL CONTEXT <span className="text-blue-400">+</span> DOCUMENT CONTEXT
            </p>
            <div className="my-1.5 text-xs text-blue-400">↓</div>
            <p className="text-xs sm:text-sm font-bold text-cyan-300 uppercase tracking-wider">
              MULTIMODAL UNDERSTANDING
            </p>
          </div>
        </div>
      </section>

      {/* ═════════════════════════════════════════════════════════
          SECTION 5 — INTELLIGENCE SHOWCASE
          ═════════════════════════════════════════════════════════ */}
      <section
        id="stage-intelligence"
        ref={setRevealRef('intelligence')}
        className="story-section relative z-10 min-h-[90vh] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 py-20"
      >
        <div className="max-w-4xl mx-auto text-center">
          <span className="text-[11px] font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">
            04 • Synthesized Intelligence
          </span>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white mt-4 tracking-tight">
            From conversation to accountability.
          </h2>
          <p className="mt-3 text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Raw audio streams are distilled into verifiable action items, approved decisions,
            topic models, and key milestones.
          </p>
        </div>

        {/* Metrics */}
        <div className="mt-12 w-full max-w-4xl grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {[
            { value: '4', label: 'Action Items', color: 'text-blue-400' },
            { value: '2', label: 'Formal Decisions', color: 'text-emerald-400' },
            { value: '8', label: 'Key Topics', color: 'text-indigo-400' },
            { value: '12', label: 'Timeline Moments', color: 'text-cyan-400' },
          ].map((m, idx) => (
            <div key={idx} className="reveal-child p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
              <span className={`text-2xl font-extrabold ${m.color}`}>{m.value}</span>
              <p className="text-[11px] font-bold uppercase text-slate-400 mt-1">{m.label}</p>
            </div>
          ))}
        </div>

        {/* Intelligence cards */}
        <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="reveal-child p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400">
              ACTION ITEMS & DELIVERABLES
            </h4>
            <div className="space-y-2 text-xs">
              {[
                { task: 'Prepare benchmark evaluation report', assignee: 'Priya Sharma', deadline: 'By tomorrow', priority: 'High' },
                { task: 'Finalize PDF download and UI layout', assignee: 'David Chen', deadline: 'By Thursday', priority: 'High' },
                { task: 'Complete integration testing', assignee: 'Project Team', deadline: 'Before Friday', priority: 'Medium' },
              ].map((item, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-slate-200">{item.task}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">👤 {item.assignee} • ⏳ {item.deadline}</p>
                  </div>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                    {item.priority}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="reveal-child p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400">
              FORMAL DECISIONS & AGREEMENTS
            </h4>
            <div className="space-y-2 text-xs">
              {[
                { decision: 'SQLite with async SQLAlchemy is persistent store for standalone faculty evaluation', context: 'Technical Architecture' },
                { decision: 'Support both cloud LLMs and local scikit-learn algorithms for offline reliability', context: 'Resilience Strategy' },
              ].map((d, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-slate-200">
                  <p className="font-semibold text-emerald-300">• {d.decision}</p>
                  <p className="text-[10px] text-slate-400 mt-1">Context: {d.context}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═════════════════════════════════════════════════════════
          SECTION 6 — AI REPORT PREVIEW
          ═════════════════════════════════════════════════════════ */}
      <section
        id="stage-report"
        ref={setRevealRef('report')}
        className="story-section relative z-10 min-h-[90vh] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 py-20"
      >
        <div className="max-w-4xl mx-auto text-center">
          <span className="text-[11px] font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/25">
            05 • Generated Report
          </span>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white mt-4 tracking-tight">
            One meeting. One structured source of truth.
          </h2>
          <p className="mt-3 text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Publication-ready ReportLab PDF reports compiled dynamically from verified analysis data.
          </p>
        </div>

        {/* Report mockup */}
        <div className="mt-12 w-full max-w-3xl p-6 sm:p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl relative scale-reveal">
          <div className="border-b border-slate-800 pb-4 mb-4 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-blue-400">
                OFFICIAL REPORTLAB PUBLICATION RECORD
              </span>
              <h3 className="text-base sm:text-lg font-bold text-white mt-0.5">
                AI-POWERED MEETING INTELLIGENCE REPORT
              </h3>
            </div>
            <span className="text-[11px] font-mono text-slate-400">Page 1 of 4</span>
          </div>

          <div className="space-y-4 text-xs text-slate-300">
            <div className="reveal-child p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-bold text-white uppercase text-[10px]">1. Executive Summary</span>
              <p className="mt-1 text-slate-400 leading-relaxed">
                The session verified complete multimodal intelligence pipeline operation,
                confirming slide transition detection and speech-to-text accuracy with
                100% offline fallback readiness.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="reveal-child p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="font-bold text-white uppercase text-[10px]">2. Key Topics</span>
                <p className="mt-1 text-slate-400">OpenCV Pipeline (95%) • Speech-to-Text (88%) • TextRank Graph (82%)</p>
              </div>
              <div className="reveal-child p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="font-bold text-white uppercase text-[10px]">3. Action Items</span>
                <p className="mt-1 text-slate-400">3 deliverables assigned with verified deadlines and evidence.</p>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
            <span className="text-[11px] text-slate-400">
              Includes two-pass page numbering, header banners, and verifiable transcript links.
            </span>
            <button
              onClick={onRunDemo}
              className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white flex items-center space-x-1.5 cursor-pointer shadow-sm"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Demo Report</span>
            </button>
          </div>
        </div>

        {/* Pipeline flow */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-2 text-xs font-mono text-slate-400 reveal-child">
          <span>INPUT</span>
          <span className="text-blue-400">→</span>
          <span>UNDERSTAND</span>
          <span className="text-blue-400">→</span>
          <span>ANALYZE</span>
          <span className="text-blue-400">→</span>
          <span className="text-emerald-400 font-bold">GENERATE</span>
        </div>
      </section>

      {/* ═════════════════════════════════════════════════════════
          SECTION 7 — FINAL CTA & UPLOAD STUDIO
          ═════════════════════════════════════════════════════════ */}
      <section
        id="stage-try"
        ref={setRevealRef('try')}
        className="story-section relative z-10 min-h-[95vh] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 py-24"
      >
        <div className="max-w-3xl mx-auto text-center mb-10">
          <span className="text-[11px] font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/25">
            06 • Analysis Studio
          </span>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white mt-4 tracking-tight">
            Ready to turn your next meeting into intelligence?
          </h2>
          <p className="mt-3 text-base text-slate-400 leading-relaxed">
            Upload your recording and let VideoIntel execute the complete multimodal pipeline.
          </p>

          <div className="mt-5 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-slate-400">
            {['Multimodal Analysis', 'AI Intelligence', 'Structured Reports', 'PDF Export'].map((feat) => (
              <span key={feat} className="flex items-center space-x-1 text-emerald-400">
                <Check className="w-3.5 h-3.5" />
                <span>{feat}</span>
              </span>
            ))}
          </div>
        </div>

        {/* Upload Studio Card */}
        <div className="w-full max-w-2xl bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative scale-reveal">
          {errorMsg && (
            <div className="mb-6 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>
              <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-rose-200">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Session Title */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">
                Meeting Session Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Executive Architecture & Planning Sync"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
            </div>

            {/* Media Upload */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">
                Meeting Video or Audio File <span className="text-rose-400">*</span>
              </label>
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDraggingMedia(true); }}
                onDragLeave={() => setIsDraggingMedia(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setIsDraggingMedia(false);
                  if (e.dataTransfer.files?.[0]) handleMediaSelect(e.dataTransfer.files[0]);
                }}
                onClick={() => mediaInputRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
                  isDraggingMedia
                    ? 'border-blue-500 bg-blue-500/10'
                    : mediaFile
                    ? 'border-emerald-500/50 bg-emerald-500/5'
                    : 'border-slate-800 bg-slate-950/60 hover:border-slate-700'
                }`}
              >
                <input
                  ref={mediaInputRef}
                  type="file"
                  accept=".mp4,.webm,.mkv,.avi,.mov,.mp3,.wav,.m4a,.ogg,.flac"
                  onChange={(e) => e.target.files?.[0] && handleMediaSelect(e.target.files[0])}
                  className="hidden"
                />
                {mediaFile ? (
                  <div className="flex items-center justify-center space-x-3 text-emerald-400">
                    <FileCheck className="w-6 h-6" />
                    <div className="text-left">
                      <p className="text-xs font-semibold text-slate-200">{mediaFile.name}</p>
                      <p className="text-[10px] text-slate-400">
                        {(mediaFile.size / (1024 * 1024)).toFixed(1)} MB • Click to replace
                      </p>
                    </div>
                  </div>
                ) : (
                  <div>
                    <Upload className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                    <p className="text-xs font-semibold text-slate-200">
                      Drag & drop your recording, or <span className="text-blue-400 hover:underline">browse files</span>
                    </p>
                    <p className="text-[10px] text-slate-500 mt-1">
                      Video (.mp4, .webm, .mkv) or Audio (.wav, .mp3) up to 500MB
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Document attachment */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">
                Supporting Document / Slide Deck <span className="text-slate-500 font-normal">(Optional)</span>
              </label>
              <div
                onClick={() => docInputRef.current?.click()}
                className={`border border-dashed rounded-xl p-3 text-center cursor-pointer transition-all ${
                  documentFile
                    ? 'border-purple-500/40 bg-purple-500/5'
                    : 'border-slate-800 bg-slate-950/40 hover:border-slate-700'
                }`}
              >
                <input
                  ref={docInputRef}
                  type="file"
                  accept=".pdf,.pptx,.ppt,.txt,.docx"
                  onChange={(e) => e.target.files?.[0] && handleDocSelect(e.target.files[0])}
                  className="hidden"
                />
                {documentFile ? (
                  <div className="flex items-center justify-center space-x-2 text-purple-400">
                    <FileText className="w-4 h-4" />
                    <span className="text-xs text-slate-200">{documentFile.name}</span>
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); setDocumentFile(null); }}
                      className="text-slate-500 hover:text-slate-300 ml-2"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-2 text-xs text-slate-400">
                    <FileText className="w-4 h-4 text-purple-400" />
                    <span>Attach slides or agenda (.pdf, .pptx, .txt) for multimodal fusion</span>
                  </div>
                )}
              </div>
            </div>

            {/* AI Provider */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  AI Intelligence Engine
                </label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value as any)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="auto">Auto (Local ML Engine Fallback)</option>
                  <option value="local_ml">Local ML Engine (100% Offline)</option>
                  <option value="openai">OpenAI (Whisper + GPT-4o)</option>
                  <option value="gemini">Google Gemini 1.5 Flash</option>
                </select>
              </div>

              {provider !== 'local_ml' && provider !== 'auto' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Custom API Key (Optional)
                  </label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-... or AIza..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center gap-3 pt-3">
              <button
                type="submit"
                disabled={isProcessing}
                className="w-full sm:flex-1 py-3 px-4 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20 transition-all flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50"
              >
                <span>Analyze Meeting Recording</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                type="button"
                onClick={onRunDemo}
                disabled={isProcessing}
                className="w-full sm:w-auto py-3 px-5 rounded-xl text-xs font-semibold bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50"
              >
                <PlayCircle className="w-4 h-4" />
                <span>Run Faculty Demo</span>
              </button>
            </div>
          </form>
        </div>
      </section>
    </div>
  );
};
