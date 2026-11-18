import React from 'react';
import { Loader2, CheckCircle2, Film, Mic, BrainCircuit, FileText, Clock } from 'lucide-react';

interface ProcessingOverlayProps {
  currentStage: number;
  elapsedSeconds: number;
}

const STAGES = [
  { label: 'Ingesting & Validating Media', desc: 'Verifying MIME integrity, audio stream, and container headers', icon: Film },
  { label: 'OpenCV Video Intelligence', desc: 'Computing frame differences, slide transitions & keyframe extraction', icon: Film },
  { label: 'Speech-to-Text Transcription', desc: 'Transcribing speech audio stream into verbatim text segments', icon: Mic },
  { label: 'AI Semantic Mining & Analysis', desc: 'Extracting Action Items, Decisions, Topics, and Sentiment metrics', icon: BrainCircuit },
  { label: 'Compiling PDF & Word Reports', desc: 'Generating publication-grade PDF & editable DOCX reports and saving to database', icon: FileText },
];

export const ProcessingOverlay: React.FC<ProcessingOverlayProps> = ({ currentStage, elapsedSeconds }) => {
  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainder = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${remainder.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
        {/* Glow accent */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 mb-3">
            <Loader2 className="w-7 h-7 animate-spin" />
          </div>
          <h3 className="text-lg font-bold text-white tracking-tight">Processing Meeting Intelligence</h3>
          <p className="text-xs text-slate-400 mt-1">
            Running real multimodal processing pipeline. Please wait while AI analyzes the session.
          </p>

          <div className="inline-flex items-center space-x-1.5 mt-3 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300 font-mono">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>Elapsed: {formatTime(elapsedSeconds)}</span>
          </div>
        </div>

        {/* Steps progression */}
        <div className="space-y-3.5">
          {STAGES.map((stage, idx) => {
            const isDone = currentStage > idx;
            const isCurrent = currentStage === idx;

            return (
              <div
                key={idx}
                className={`flex items-start space-x-3 p-3 rounded-xl border transition-all ${
                  isCurrent
                    ? 'bg-blue-950/40 border-blue-500/40 shadow-sm shadow-blue-500/10'
                    : isDone
                    ? 'bg-slate-800/40 border-slate-700/40'
                    : 'bg-slate-900/40 border-slate-800/30 opacity-50'
                }`}
              >
                <div className="mt-0.5">
                  {isDone ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : isCurrent ? (
                    <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border border-slate-600 flex items-center justify-center text-[10px] text-slate-400">
                      {idx + 1}
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span
                      className={`text-xs font-semibold ${
                        isCurrent ? 'text-blue-300' : isDone ? 'text-slate-200' : 'text-slate-400'
                      }`}
                    >
                      {stage.label}
                    </span>
                    {isCurrent && (
                      <span className="text-[10px] text-blue-400 font-mono animate-pulse">Running</span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-tight">{stage.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 text-center">
          <span className="text-[11px] text-slate-400">
            OpenCV Keyframes • Speech-to-Text • Scikit-Learn / LLM • ReportLab & python-docx
          </span>
        </div>
      </div>
    </div>
  );
};
