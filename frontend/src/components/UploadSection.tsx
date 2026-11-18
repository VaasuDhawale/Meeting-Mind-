import React, { useState, useRef } from 'react';
import {
  Upload,
  Video,
  FileText,
  Cpu,
  Sparkles,
  AlertCircle,
  X,
  Play,
  FileCheck,
} from 'lucide-react';

interface UploadSectionProps {
  onSubmit: (formData: FormData) => void;
  onRunDemo: () => void;
  isProcessing: boolean;
}

export const UploadSection: React.FC<UploadSectionProps> = ({
  onSubmit,
  onRunDemo,
  isProcessing,
}) => {
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

  const validateFile = (file: File, allowedExts: string[], maxMb: number): string | null => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedExts.includes(ext)) {
      return `Invalid format '${ext}'. Allowed: ${allowedExts.join(', ')}`;
    }
    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > maxMb) {
      return `File size (${sizeMb.toFixed(1)}MB) exceeds maximum ${maxMb}MB limit.`;
    }
    return null;
  };

  const handleMediaSelect = (file: File) => {
    const err = validateFile(file, allowedMediaExts, 500);
    if (err) {
      setErrorMsg(err);
      return;
    }
    setErrorMsg(null);
    setMediaFile(file);
  };

  const handleDocSelect = (file: File) => {
    const err = validateFile(file, allowedDocExts, 50);
    if (err) {
      setErrorMsg(err);
      return;
    }
    setErrorMsg(null);
    setDocumentFile(file);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!mediaFile) {
      setErrorMsg('Please select a video or audio file to analyze.');
      return;
    }
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('title', title.trim() || 'Meeting Intelligence Session');
    formData.append('file', mediaFile);
    if (documentFile) {
      formData.append('document', documentFile);
    }
    if (provider !== 'auto') {
      formData.append('provider', provider);
    }
    if (apiKey.trim()) {
      formData.append('api_key', apiKey.trim());
    }

    onSubmit(formData);
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      {/* Intro Banner */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/25 text-blue-400 text-xs font-semibold mb-3 shadow-sm">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Multimodal Meeting Intelligence Engine • Final Year Evaluation</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          Transform Multimodal Meetings into Persistent Intelligence
        </h1>
        <p className="mt-2 text-sm text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Ingest raw meeting video or audio recordings. Computer vision analyzes slide transitions, speech-to-text transcribes discussion, and algorithmic NLP mines actionable deliverables and formal agreements into an exportable PDF report.
        </p>
      </div>

      {/* 4-Step Demonstration Workflow Card (For Faculty Review) */}
      <div className="mb-6 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-3 text-center sm:text-left">
          Core System Pipeline Architecture
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
            <span className="text-[10px] font-mono font-bold text-rose-400 px-1.5 py-0.5 rounded bg-rose-500/10 border border-rose-500/20">
              1. THE PROBLEM
            </span>
            <p className="text-xs font-semibold text-slate-200 mt-2">Unstructured Sessions</p>
            <p className="text-[11px] text-slate-400 mt-1 leading-snug">
              Hours of meetings lost without searchable notes, action item accountability, or slide context.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
            <span className="text-[10px] font-mono font-bold text-blue-400 px-1.5 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">
              2. USER INPUT
            </span>
            <p className="text-xs font-semibold text-slate-200 mt-2">Media & Agenda</p>
            <p className="text-[11px] text-slate-400 mt-1 leading-snug">
              Video / Audio recording (.mp4, .wav) with optional supporting agenda presentation (.pdf, .txt).
            </p>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
            <span className="text-[10px] font-mono font-bold text-indigo-400 px-1.5 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
              3. AI/ML PIPELINE
            </span>
            <p className="text-xs font-semibold text-slate-200 mt-2">Multimodal Synthesis</p>
            <p className="text-[11px] text-slate-400 mt-1 leading-snug">
              OpenCV slide shift detection + Speech-to-Text + scikit-learn TF-IDF & TextRank graph summarizer.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
            <span className="text-[10px] font-mono font-bold text-emerald-400 px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
              4. OUTPUT REPORT
            </span>
            <p className="text-xs font-semibold text-slate-200 mt-2">Actionable Intelligence</p>
            <p className="text-[11px] text-slate-400 mt-1 leading-snug">
              Executive summary, assigned action items table, agreements, keyframes, and ReportLab PDF.
            </p>
          </div>
        </div>
      </div>

      {/* Faculty Demo Banner Card */}
      <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-amber-500/15 via-orange-500/10 to-slate-900 border border-amber-500/30 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-lg">
        <div className="flex items-start space-x-3">
          <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 mt-0.5">
            <Play className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-bold text-amber-200">FACULTY DEMO FAST-TRACK</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono border border-amber-500/30">
                DEMO INPUT
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              Instantly test the real end-to-end pipeline using pre-generated meeting video with slide transitions, audio waveform, and agenda document.
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={onRunDemo}
          disabled={isProcessing}
          className="whitespace-nowrap px-4 py-2.5 rounded-lg text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20 transition-all cursor-pointer disabled:opacity-50"
        >
          ⚡ Load & Run Demo
        </button>
      </div>

      {/* Main Upload Form Card */}
      <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl">
        {/* Error Alert */}
        {errorMsg && (
          <div className="mb-6 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center space-x-3 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-400" />
            <span className="flex-1">{errorMsg}</span>
            <button type="button" onClick={() => setErrorMsg(null)}>
              <X className="w-4 h-4 text-rose-400 hover:text-rose-200" />
            </button>
          </div>
        )}

        {/* Meeting Title Input */}
        <div className="mb-6">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            Meeting / Session Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Sprint Planning & Technical Review"
            className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500 transition-colors"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Media File Upload (Primary) */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span className="flex items-center space-x-1.5">
                <Video className="w-3.5 h-3.5 text-blue-400" />
                <span>Video / Audio File (Required)</span>
              </span>
              <span className="text-[10px] text-slate-400">Max 500MB</span>
            </label>

            <input
              type="file"
              ref={mediaInputRef}
              accept="video/*,audio/*"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleMediaSelect(e.target.files[0]);
                }
              }}
            />

            {!mediaFile ? (
              <div
                onClick={() => mediaInputRef.current?.click()}
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDraggingMedia(true);
                }}
                onDragLeave={() => setIsDraggingMedia(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setIsDraggingMedia(false);
                  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    handleMediaSelect(e.dataTransfer.files[0]);
                  }
                }}
                className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
                  isDraggingMedia
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-slate-700/80 bg-slate-950/50 hover:border-slate-600 hover:bg-slate-950'
                }`}
              >
                <Upload className="w-8 h-8 text-blue-400 mx-auto mb-2 opacity-80" />
                <p className="text-xs font-medium text-slate-200">Click to browse or drop file here</p>
                <p className="text-[11px] text-slate-400 mt-1">
                  MP4, WEBM, MKV, MOV, MP3, WAV, M4A
                </p>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-slate-950 border border-blue-500/30 flex items-center justify-between">
                <div className="flex items-center space-x-3 overflow-hidden">
                  <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400">
                    <Video className="w-5 h-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-semibold text-white truncate">{mediaFile.name}</p>
                    <p className="text-[10px] text-slate-400">{(mediaFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setMediaFile(null)}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Supporting Document Upload (Optional) */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span className="flex items-center space-x-1.5">
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                <span>Supporting Document (Optional)</span>
              </span>
              <span className="text-[10px] text-slate-400">Max 50MB</span>
            </label>

            <input
              type="file"
              ref={docInputRef}
              accept=".pdf,.pptx,.ppt,.txt,.docx"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleDocSelect(e.target.files[0]);
                }
              }}
            />

            {!documentFile ? (
              <div
                onClick={() => docInputRef.current?.click()}
                className="border-2 border-dashed border-slate-700/80 bg-slate-950/50 hover:border-slate-600 hover:bg-slate-950 rounded-xl p-6 text-center cursor-pointer transition-all"
              >
                <FileText className="w-8 h-8 text-cyan-400 mx-auto mb-2 opacity-80" />
                <p className="text-xs font-medium text-slate-200">Attach presentation, agenda or notes</p>
                <p className="text-[11px] text-slate-400 mt-1">PDF, PPTX, TXT, DOCX</p>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-slate-950 border border-cyan-500/30 flex items-center justify-between">
                <div className="flex items-center space-x-3 overflow-hidden">
                  <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-400">
                    <FileCheck className="w-5 h-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-semibold text-white truncate">{documentFile.name}</p>
                    <p className="text-[10px] text-slate-400">{(documentFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setDocumentFile(null)}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* AI Processing Engine Configuration */}
        <div className="mb-6 p-4 rounded-xl bg-slate-950/60 border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>AI Intelligence Engine</span>
            </span>
            <span className="text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              Offline Local ML Available
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 mb-3">
            <label
              className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                provider === 'auto'
                  ? 'bg-blue-600/15 border-blue-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <input
                type="radio"
                name="provider"
                value="auto"
                checked={provider === 'auto'}
                onChange={() => setProvider('auto')}
                className="hidden"
              />
              <p className="font-semibold text-white">Auto Intelligence</p>
              <p className="text-[10px] text-slate-400 mt-0.5">Cloud LLM if key present, else Local ML</p>
            </label>

            <label
              className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                provider === 'local_ml'
                  ? 'bg-blue-600/15 border-blue-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <input
                type="radio"
                name="provider"
                value="local_ml"
                checked={provider === 'local_ml'}
                onChange={() => setProvider('local_ml')}
                className="hidden"
              />
              <p className="font-semibold text-white">Local ML / TextRank</p>
              <p className="text-[10px] text-slate-400 mt-0.5">Zero cloud calls, 100% offline scikit-learn</p>
            </label>

            <label
              className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                provider === 'openai'
                  ? 'bg-blue-600/15 border-blue-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <input
                type="radio"
                name="provider"
                value="openai"
                checked={provider === 'openai'}
                onChange={() => setProvider('openai')}
                className="hidden"
              />
              <p className="font-semibold text-white">OpenAI GPT-4o-mini</p>
              <p className="text-[10px] text-slate-400 mt-0.5">Cloud generative intelligence synthesis</p>
            </label>
          </div>

          {(provider === 'openai' || provider === 'gemini') && (
            <div className="mt-3 pt-3 border-t border-slate-800">
              <label className="block text-[11px] text-slate-400 mb-1">
                Optional API Key (or leave blank to use backend .env setting):
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-white text-xs font-mono focus:outline-none focus:border-blue-500"
              />
            </div>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isProcessing || !mediaFile}
          className="w-full py-3.5 px-6 rounded-xl font-bold text-sm bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:via-indigo-500 hover:to-cyan-400 text-white shadow-lg shadow-blue-500/25 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          <Sparkles className="w-4 h-4" />
          <span>Execute Multimodal Intelligence Analysis</span>
        </button>
      </form>
    </div>
  );
};
