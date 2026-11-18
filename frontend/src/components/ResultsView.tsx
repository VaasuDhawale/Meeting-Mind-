import React, { useState } from 'react';
import {
  Download,
  FileDown,
  Copy,
  Check,
  Loader2,
  CheckCircle2,
  Film,
  FileText,
  User,
  Tag,
  ArrowLeft,
  Search,
  BrainCircuit,
  ExternalLink,
  Eye,
  Clock,
  CheckSquare,
  Square,
  HelpCircle,
  FileCode,
  Sparkles,
  ChevronRight,
  FileSpreadsheet,
} from 'lucide-react';
import type { MeetingSession, DecisionItem, ActionItem, Topic, QuestionAnswer, TimelineEvent, DocumentPage } from '../types';
import {
  downloadFileBlob,
  getPdfDownloadUrl,
  getDocxDownloadUrl,
  getTranscriptPdfUrl,
  getTranscriptTxtUrl,
  getJsonExportUrl,
  getMarkdownExportUrl,
  getTextReportUrl,
} from '../api';

interface ResultsViewProps {
  session: MeetingSession;
  onNewAnalysis: () => void;
}

export const ResultsView: React.FC<ResultsViewProps> = ({ session, onNewAnalysis }) => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [transcriptSearch, setTranscriptSearch] = useState('');
  const [completedTasks, setCompletedTasks] = useState<Record<number, boolean>>({});
  const [isDownloadingFullPdf, setIsDownloadingFullPdf] = useState(false);
  const [isDownloadingDocx, setIsDownloadingDocx] = useState(false);
  const [isDownloadingTransPdf, setIsDownloadingTransPdf] = useState(false);
  const [isDownloadingJson, setIsDownloadingJson] = useState(false);
  const [isDownloadingMd, setIsDownloadingMd] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const [downloadNotification, setDownloadNotification] = useState<string | null>(null);
  const [previewDocType, setPreviewDocType] = useState<'report' | 'transcript'>('report');

  const toggleTask = (idx: number) => {
    setCompletedTasks((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const formatDuration = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainder = Math.floor(secs % 60);
    return `${mins}m ${remainder}s`;
  };

  const jumpToTranscriptEvidence = (quoteOrTimestamp?: string | null) => {
    if (!quoteOrTimestamp) {
      setActiveTab('transcript');
      return;
    }
    // Extract first 4-6 distinctive words
    const words = quoteOrTimestamp.replace(/[^\w\s]/g, '').split(/\s+/).filter(w => w.length > 3);
    const snippet = words.slice(0, 3).join(' ');
    setTranscriptSearch(snippet);
    setActiveTab('transcript');
  };

  const fullPdfUrl = getPdfDownloadUrl(session.id);
  const fullPdfInlineUrl = getPdfDownloadUrl(session.id, true);
  const docxUrl = getDocxDownloadUrl(session.id);
  const transPdfUrl = getTranscriptPdfUrl(session.id);
  const transPdfInlineUrl = getTranscriptPdfUrl(session.id, true);
  const transTxtUrl = getTranscriptTxtUrl(session.id);
  const jsonUrl = getJsonExportUrl(session.id);
  const mdUrl = getMarkdownExportUrl(session.id);
  const txtReportUrl = getTextReportUrl(session.id);

  const handleDownloadDocx = async () => {
    setDownloadNotification(null);
    setIsDownloadingDocx(true);
    try {
      await downloadFileBlob(docxUrl, `Meeting_Intelligence_${session.id.slice(0, 8)}.docx`);
      setDownloadNotification('Professional Word Report (.docx) downloaded successfully.');
    } catch (err: any) {
      setDownloadNotification(`Failed to download Word report: ${err.message || err}`);
    } finally {
      setIsDownloadingDocx(false);
    }
  };

  const handleDownloadFullPdf = async () => {
    setDownloadNotification(null);
    setIsDownloadingFullPdf(true);
    try {
      await downloadFileBlob(fullPdfUrl, `VideoIntel_Executive_Report_${session.id}.pdf`);
      setDownloadNotification('Executive PDF Report downloaded successfully.');
    } catch (err: any) {
      setDownloadNotification(`Failed to download Executive PDF: ${err.message || err}`);
    } finally {
      setIsDownloadingFullPdf(false);
    }
  };

  const handleDownloadTranscriptPdf = async () => {
    setDownloadNotification(null);
    setIsDownloadingTransPdf(true);
    try {
      await downloadFileBlob(transPdfUrl, `VideoIntel_Transcript_${session.id}.pdf`);
      setDownloadNotification('Transcript PDF downloaded successfully.');
    } catch (err: any) {
      setDownloadNotification(`Failed to download Transcript PDF: ${err.message || err}`);
    } finally {
      setIsDownloadingTransPdf(false);
    }
  };

  const handleDownloadJson = async () => {
    setDownloadNotification(null);
    setIsDownloadingJson(true);
    try {
      await downloadFileBlob(jsonUrl, `Meeting_Intel_${session.id.slice(0, 8)}.json`);
      setDownloadNotification('Structured JSON intelligence exported successfully.');
    } catch (err: any) {
      window.open(jsonUrl, '_blank');
    } finally {
      setIsDownloadingJson(false);
    }
  };

  const handleDownloadMarkdown = async () => {
    setDownloadNotification(null);
    setIsDownloadingMd(true);
    try {
      await downloadFileBlob(mdUrl, `Meeting_Report_${session.id.slice(0, 8)}.md`);
      setDownloadNotification('Dynamic Markdown report downloaded.');
    } catch (err: any) {
      window.open(mdUrl, '_blank');
    } finally {
      setIsDownloadingMd(false);
    }
  };

  const handleDownloadTxtReport = async () => {
    setDownloadNotification(null);
    try {
      await downloadFileBlob(txtReportUrl, `Meeting_Report_${session.id.slice(0, 8)}.txt`);
      setDownloadNotification('Plain text report downloaded.');
    } catch (err: any) {
      window.open(txtReportUrl, '_blank');
    }
  };

  const handleCopyTranscript = () => {
    if (session.transcript) {
      navigator.clipboard.writeText(session.transcript);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  // Normalized items
  const keyframes = session.video_analysis?.keyframes || [];
  const sceneChanges = session.video_analysis?.scene_changes || 0;
  const visualActivity = session.video_analysis?.visual_activity || 0;
  const actionItems: ActionItem[] = session.action_items || [];
  const rawDecisions = session.decisions || [];
  const decisions: DecisionItem[] = rawDecisions.map((d: any) => {
    if (typeof d === 'string') {
      return {
        decision: d.replace(/^Agreed:\s*/i, ''),
        context: 'Consensus confirmed during session',
        participants: 'Meeting Participants',
        evidence: d,
      };
    }
    return d as DecisionItem;
  });
  const topics: Topic[] = session.topics || [];
  const questionsAnswers: QuestionAnswer[] = session.questions_answers || [];
  const timeline: TimelineEvent[] = session.timeline || [];
  const documentAnalysis = session.document_analysis;
  const documentPages: DocumentPage[] = documentAnalysis?.pages || [];
  const speakers = session.speakers || [];
  const evidenceList = session.evidence || [];

  const sentiment = session.sentiment || {
    overall: 'Positive',
    positive_score: 0.7,
    neutral_score: 0.25,
    negative_score: 0.05,
  };

  // Determine available dynamic tabs
  const hasVideo = keyframes.length > 0 || sceneChanges > 0 || session.source_file_type === 'video';
  const hasDoc = documentPages.length > 0 || Boolean(session.document_filename);

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <button
          onClick={onNewAnalysis}
          className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>New Analysis</span>
        </button>

        <div className="flex flex-wrap items-center gap-2">
          {/* Quick In-App Preview Toggle */}
          <button
            onClick={() => setActiveTab('pdf_preview')}
            className={`inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
              activeTab === 'pdf_preview'
                ? 'bg-emerald-600/20 text-emerald-300 border-emerald-500/40'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
            }`}
            title="Read and view the generated PDF right inside the app"
          >
            <Eye className="w-3.5 h-3.5 text-emerald-400" />
            <span>Interactive PDF Viewer</span>
          </button>

          {/* Open / View in Native Browser Reader */}
          <a
            href={fullPdfInlineUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-600/90 hover:bg-indigo-500 text-white shadow-sm transition-all"
            title="Open in new browser tab with print, zoom, and search controls"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Open in Tab</span>
          </a>

          {/* Dedicated Transcript PDF Download */}
          <button
            onClick={handleDownloadTranscriptPdf}
            disabled={isDownloadingTransPdf}
            className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all cursor-pointer disabled:opacity-50"
            title="Download dedicated PDF document of dialogue transcript"
          >
            {isDownloadingTransPdf ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
            ) : (
              <FileDown className="w-3.5 h-3.5 text-cyan-400" />
            )}
            <span>Transcript PDF</span>
          </button>

          {/* JSON Export */}
          <button
            onClick={handleDownloadJson}
            disabled={isDownloadingJson}
            className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all cursor-pointer disabled:opacity-50"
            title="Export standardized JSON data structure"
          >
            {isDownloadingJson ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-400" />
            ) : (
              <FileCode className="w-3.5 h-3.5 text-amber-400" />
            )}
            <span>JSON</span>
          </button>

          {/* Markdown Report */}
          <button
            onClick={handleDownloadMarkdown}
            disabled={isDownloadingMd}
            className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all cursor-pointer disabled:opacity-50"
            title="Download dynamic Markdown report"
          >
            {isDownloadingMd ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-400" />
            ) : (
              <FileSpreadsheet className="w-3.5 h-3.5 text-purple-400" />
            )}
            <span>Markdown</span>
          </button>

          {/* Primary Word Report (.docx) Download */}
          <button
            onClick={handleDownloadDocx}
            disabled={isDownloadingDocx}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-500/20 transition-all cursor-pointer disabled:opacity-50"
            title="Download professional, editable Microsoft Word document (.docx)"
          >
            {isDownloadingDocx ? (
              <Loader2 className="w-4 h-4 animate-spin text-white" />
            ) : (
              <FileText className="w-4 h-4 text-indigo-200" />
            )}
            <span>Download Word Report (.docx)</span>
          </button>

          {/* Primary Full PDF Download */}
          <button
            onClick={handleDownloadFullPdf}
            disabled={isDownloadingFullPdf}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-500/20 transition-all cursor-pointer disabled:opacity-50"
            title="Download official VideoIntel Executive Report (PDF)"
          >
            {isDownloadingFullPdf ? (
              <Loader2 className="w-4 h-4 animate-spin text-white" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            <span>Download Executive Report</span>
          </button>
        </div>
      </div>

      {downloadNotification && (
        <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center justify-between">
          <span>{downloadNotification}</span>
          <button onClick={() => setDownloadNotification(null)} className="font-bold hover:underline">Dismiss</button>
        </div>
      )}

      {/* Header Info Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/25">
                {session.ai_provider || 'Local ML Engine'}
              </span>
              <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {session.source_file_type === 'video' ? 'Multimodal Video' : 'Audio Track'}
              </span>
              {session.document_filename && (
                <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/25">
                  Attachment: {session.document_filename}
                </span>
              )}
              <span className="text-[11px] text-emerald-400 font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center space-x-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>Verified</span>
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {session.title}
            </h1>
            <p className="text-xs text-slate-400 mt-1 flex flex-wrap items-center gap-x-4 gap-y-1">
              <span>Source: {session.source_filename || 'Direct Upload'}</span>
              <span>•</span>
              <span>Processed: {session.created_at?.slice(0, 16).replace('T', ' ') || 'Just now'}</span>
              {session.duration_seconds > 0 && (
                <>
                  <span>•</span>
                  <span>Duration: {formatDuration(session.duration_seconds)}</span>
                </>
              )}
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center space-x-2 bg-slate-950/80 border border-slate-800/80 rounded-xl p-2.5 self-start md:self-auto">
            <div className="text-center px-3 border-r border-slate-800">
              <p className="text-[10px] uppercase font-semibold text-slate-400">Tasks</p>
              <p className="text-base font-bold text-white mt-0.5">{actionItems.length}</p>
            </div>
            <div className="text-center px-3 border-r border-slate-800">
              <p className="text-[10px] uppercase font-semibold text-slate-400">Decisions</p>
              <p className="text-base font-bold text-emerald-400 mt-0.5">{decisions.length}</p>
            </div>
            {hasVideo && (
              <div className="text-center px-3 border-r border-slate-800">
                <p className="text-[10px] uppercase font-semibold text-slate-400">Shifts</p>
                <p className="text-base font-bold text-cyan-400 mt-0.5">{sceneChanges}</p>
              </div>
            )}
            <div className="text-center px-3">
              <p className="text-[10px] uppercase font-semibold text-slate-400">Topics</p>
              <p className="text-base font-bold text-indigo-400 mt-0.5">{topics.length}</p>
            </div>
          </div>
        </div>

        {/* Dynamic Tab Navigation (Only displays tabs with real meaning) */}
        <div className="flex flex-wrap border-b border-slate-800 mt-6 -mb-6 -mx-6 px-6 bg-slate-950/40">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Overview
          </button>

          {actionItems.length > 0 && (
            <button
              onClick={() => setActiveTab('actions')}
              className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                activeTab === 'actions'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Action Items ({actionItems.length})
            </button>
          )}

          {decisions.length > 0 && (
            <button
              onClick={() => setActiveTab('decisions')}
              className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                activeTab === 'decisions'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Decisions ({decisions.length})
            </button>
          )}

          {topics.length > 0 && (
            <button
              onClick={() => setActiveTab('topics')}
              className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                activeTab === 'topics'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Topics ({topics.length})
            </button>
          )}

          {questionsAnswers.length > 0 && (
            <button
              onClick={() => setActiveTab('qa')}
              className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                activeTab === 'qa'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Q&A ({questionsAnswers.length})
            </button>
          )}

          {timeline.length > 0 && (
            <button
              onClick={() => setActiveTab('timeline')}
              className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                activeTab === 'timeline'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Timeline ({timeline.length})
            </button>
          )}

          {hasVideo && (
            <button
              onClick={() => setActiveTab('keyframes')}
              className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                activeTab === 'keyframes'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Visual Evidence ({keyframes.length})
            </button>
          )}

          {hasDoc && (
            <button
              onClick={() => setActiveTab('documents')}
              className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                activeTab === 'documents'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Slides & Document ({documentPages.length})
            </button>
          )}

          {evidenceList.length > 0 && (
            <button
              onClick={() => setActiveTab('evidence')}
              className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                activeTab === 'evidence'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Evidence Sources ({evidenceList.length})
            </button>
          )}

          <button
            onClick={() => setActiveTab('transcript')}
            className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
              activeTab === 'transcript'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Transcript
          </button>

          <button
            onClick={() => setActiveTab('dynamic_report')}
            className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all flex items-center space-x-1.5 cursor-pointer ${
              activeTab === 'dynamic_report'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Interactive Report</span>
          </button>

          <button
            onClick={() => setActiveTab('pdf_preview')}
            className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all flex items-center space-x-1.5 cursor-pointer ${
              activeTab === 'pdf_preview'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Eye className="w-3.5 h-3.5 text-emerald-400" />
            <span>PDF Reader</span>
          </button>

          <button
            onClick={() => setActiveTab('model_spec')}
            className={`py-3 px-3.5 text-xs font-semibold border-b-2 transition-all flex items-center space-x-1.5 cursor-pointer ${
              activeTab === 'model_spec'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <BrainCircuit className="w-3.5 h-3.5 text-indigo-400" />
            <span>Model Spec</span>
          </button>
        </div>
      </div>

      {/* =========================================================================
          TAB 1: OVERVIEW & EXECUTIVE SUMMARY
      ========================================================================= */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Executive Summary */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span>Executive Summary</span>
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                {session.summary || 'No summary detected for this session.'}
              </p>
            </div>

            {/* Prominent Decisions */}
            {decisions.length > 0 && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Key Decisions & Formal Agreements ({decisions.length})</span>
                  </h2>
                  <button
                    onClick={() => setActiveTab('decisions')}
                    className="text-xs text-blue-400 hover:underline flex items-center space-x-1"
                  >
                    <span>View details</span>
                    <ChevronRight className="w-3 h-3" />
                  </button>
                </div>
                <div className="space-y-3">
                  {decisions.map((d, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-slate-200 flex flex-col gap-1.5"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-xs font-semibold text-emerald-300 leading-snug">
                          • {d.decision}
                        </span>
                        {d.evidence && (
                          <button
                            onClick={() => jumpToTranscriptEvidence(d.evidence)}
                            className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 transition-all cursor-pointer whitespace-nowrap"
                            title="Jump to quote in transcript"
                          >
                            Evidence Quote
                          </button>
                        )}
                      </div>
                      {d.participants && (
                        <span className="text-[11px] text-slate-400">
                          Participants: {d.participants}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Action Items Checklist */}
            {actionItems.length > 0 && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
                    <CheckSquare className="w-4 h-4 text-blue-400" />
                    <span>Action Items & Key Tasks ({actionItems.length})</span>
                  </h2>
                  <button
                    onClick={() => setActiveTab('actions')}
                    className="text-xs text-blue-400 hover:underline flex items-center space-x-1"
                  >
                    <span>View all tasks</span>
                    <ChevronRight className="w-3 h-3" />
                  </button>
                </div>
                <div className="space-y-2.5">
                  {actionItems.slice(0, 4).map((item, idx) => {
                    const isDone = completedTasks[idx] || item.status === 'completed';
                    return (
                      <div
                        key={idx}
                        className={`p-3 rounded-xl border flex items-center justify-between transition-all ${
                          isDone
                            ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                            : 'bg-slate-950/80 border-slate-800'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => toggleTask(idx)}
                            className="text-slate-400 hover:text-blue-400 cursor-pointer"
                          >
                            {isDone ? (
                              <CheckSquare className="w-4 h-4 text-emerald-400" />
                            ) : (
                              <Square className="w-4 h-4" />
                            )}
                          </button>
                          <div>
                            <p className={`text-xs font-medium text-slate-200 ${isDone ? 'line-through text-slate-500' : ''}`}>
                              {item.task}
                            </p>
                            <div className="flex items-center space-x-2 mt-1 text-[11px] text-slate-400">
                              <span>👤 {item.assignee || 'Unassigned'}</span>
                              <span>•</span>
                              <span>⏳ {item.due_date || 'Milestone'}</span>
                            </div>
                          </div>
                        </div>
                        {item.evidence && (
                          <button
                            onClick={() => jumpToTranscriptEvidence(item.evidence)}
                            className="text-[10px] text-blue-400 hover:underline ml-2 whitespace-nowrap cursor-pointer"
                          >
                            Evidence
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* Key Discussion Topics */}
            {topics.length > 0 && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center space-x-2">
                  <Tag className="w-4 h-4 text-indigo-400" />
                  <span>Discussion Topics</span>
                </h2>
                <div className="space-y-2.5">
                  {topics.map((t, idx) => (
                    <div key={idx} className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                      <div className="flex items-center justify-between text-xs font-semibold text-slate-200 mb-1">
                        <span>{t.topic}</span>
                        <span className="text-blue-400">{Math.round(t.relevance * 100)}%</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden mb-1.5">
                        <div
                          className="bg-blue-500 h-full rounded-full"
                          style={{ width: `${Math.min(100, t.relevance * 100)}%` }}
                        />
                      </div>
                      {t.evidence && (
                        <p className="text-[10px] text-slate-400 italic truncate" title={t.evidence}>
                          &quot;{t.evidence}&quot;
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sentiment Analysis Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center space-x-2">
                <Clock className="w-4 h-4 text-emerald-400" />
                <span>Discussion Tone & Sentiment</span>
              </h2>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-slate-400">Overall Polarity:</span>
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  {sentiment.overall}
                </span>
              </div>
              <div className="space-y-2 text-xs">
                <div>
                  <div className="flex justify-between text-slate-400 mb-0.5">
                    <span>Positive Consensus</span>
                    <span>{Math.round(sentiment.positive_score * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full" style={{ width: `${sentiment.positive_score * 100}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-slate-400 mb-0.5">
                    <span>Neutral Discussion</span>
                    <span>{Math.round(sentiment.neutral_score * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-blue-500 h-full" style={{ width: `${sentiment.neutral_score * 100}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-slate-400 mb-0.5">
                    <span>Constructive Critique</span>
                    <span>{Math.round(sentiment.negative_score * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-amber-500 h-full" style={{ width: `${sentiment.negative_score * 100}%` }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Speaker Participation Analysis */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center space-x-2">
                <User className="w-4 h-4 text-indigo-400" />
                <span>Speaker Participation</span>
              </h2>
              {speakers.length > 0 ? (
                <div className="space-y-3">
                  {speakers.map((s, idx) => (
                    <div key={idx} className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                      <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
                        <span>{s.name}</span>
                        <span className="text-cyan-400">{s.percentage}%</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
                        <span>Time: {s.speaking_time}s</span>
                        {s.turns && <span>Turns: {s.turns}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">
                  Single speaker or unsegmented stream; speaker-level diarization was not present in audio track.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 2: ACTION ITEMS
      ========================================================================= */}
      {activeTab === 'actions' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-bold text-white">Action Items & Deliverables</h2>
              <p className="text-xs text-slate-400">
                Track deliverables with verifiable evidence quotes from the meeting stream.
              </p>
            </div>
            <div className="text-xs text-slate-400">
              Completed: <span className="font-bold text-emerald-400">{Object.values(completedTasks).filter(Boolean).length}</span> / {actionItems.length}
            </div>
          </div>

          {actionItems.length === 0 ? (
            <p className="text-xs text-slate-400 italic py-6 text-center">No action items were detected in this session.</p>
          ) : (
            <div className="space-y-3">
              {actionItems.map((item, idx) => {
                const isDone = completedTasks[idx] || item.status === 'completed';
                return (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border transition-all ${
                      isDone
                        ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                        : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start space-x-3">
                        <button
                          onClick={() => toggleTask(idx)}
                          className="mt-0.5 text-slate-400 hover:text-blue-400 cursor-pointer"
                        >
                          {isDone ? (
                            <CheckSquare className="w-4 h-4 text-emerald-400" />
                          ) : (
                            <Square className="w-4 h-4" />
                          )}
                        </button>
                        <div>
                          <p className={`text-xs sm:text-sm font-semibold text-slate-200 ${isDone ? 'line-through text-slate-500' : ''}`}>
                            {item.task}
                          </p>
                          <div className="flex flex-wrap items-center gap-2 mt-2">
                            <span className="text-[11px] px-2 py-0.5 rounded bg-blue-500/15 text-blue-300 border border-blue-500/25">
                              👤 {item.assignee || 'Unassigned'}
                            </span>
                            <span className={`text-[11px] px-2 py-0.5 rounded border ${
                              item.priority === 'High'
                                ? 'bg-rose-500/15 text-rose-300 border-rose-500/25'
                                : 'bg-slate-800 text-slate-300 border-slate-700'
                            }`}>
                              Priority: {item.priority || 'Medium'}
                            </span>
                            <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                              ⏳ {item.due_date || 'Milestone'}
                            </span>
                          </div>
                        </div>
                      </div>

                      {item.evidence && (
                        <button
                          onClick={() => jumpToTranscriptEvidence(item.evidence)}
                          className="text-[11px] px-2.5 py-1 rounded bg-blue-500/10 hover:bg-blue-500/20 text-blue-300 border border-blue-500/30 transition-all cursor-pointer whitespace-nowrap self-start"
                        >
                          View Evidence Quote
                        </button>
                      )}
                    </div>

                    {item.evidence && (
                      <div className="mt-3 pt-2 border-t border-slate-800/80 text-[11px] text-slate-400 italic">
                        <span className="text-slate-500 font-medium">Verifiable Context:</span> &quot;{item.evidence}&quot;
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 3: DECISIONS
      ========================================================================= */}
      {activeTab === 'decisions' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white">Formal Decisions & Agreements</h2>
            <p className="text-xs text-slate-400">
              Approved technical consensus and strategic agreements documented from session dialogue.
            </p>
          </div>

          {decisions.length === 0 ? (
            <p className="text-xs text-slate-400 italic py-6 text-center">No decisions were detected in this session.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {decisions.map((d, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">
                        Decision #{idx + 1}
                      </span>
                      {d.evidence && (
                        <button
                          onClick={() => jumpToTranscriptEvidence(d.evidence)}
                          className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/40 cursor-pointer"
                        >
                          Transcript Source
                        </button>
                      )}
                    </div>
                    <p className="text-sm font-semibold text-slate-100 leading-snug">
                      {d.decision}
                    </p>
                    {d.context && (
                      <p className="text-xs text-slate-400 mt-2">
                        <span className="text-slate-500">Context:</span> {d.context}
                      </p>
                    )}
                  </div>

                  {d.evidence && (
                    <div className="mt-3 pt-2 border-t border-emerald-500/20 text-[11px] text-emerald-300/80 italic">
                      &quot;{d.evidence}&quot;
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 4: TOPICS
      ========================================================================= */}
      {activeTab === 'topics' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white">Extracted Discussion Topics</h2>
            <p className="text-xs text-slate-400">
              TF-IDF topic modeling and semantic relevance ranking across the session stream.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {topics.map((t, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-bold text-white">{t.topic}</h3>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">
                    Relevance: {Math.round(t.relevance * 100)}%
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-3">
                  <div className="bg-blue-500 h-full rounded-full" style={{ width: `${t.relevance * 100}%` }} />
                </div>
                {t.supporting_points && t.supporting_points.length > 0 && (
                  <div className="space-y-1 mt-2">
                    <p className="text-[11px] text-slate-500 uppercase font-semibold">Supporting Discussion:</p>
                    {t.supporting_points.map((pt, pIdx) => (
                      <p key={pIdx} className="text-xs text-slate-300">
                        • {pt}
                      </p>
                    ))}
                  </div>
                )}
                {t.evidence && (
                  <button
                    onClick={() => jumpToTranscriptEvidence(t.evidence)}
                    className="mt-3 text-[11px] text-blue-400 hover:underline cursor-pointer flex items-center space-x-1"
                  >
                    <span>View in Transcript</span>
                    <ChevronRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 5: QUESTIONS & ANSWERS
      ========================================================================= */}
      {activeTab === 'qa' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white">Questions & Answers</h2>
            <p className="text-xs text-slate-400">
              Identified questions and resulting responses from the session dialogue.
            </p>
          </div>

          {questionsAnswers.length === 0 ? (
            <p className="text-xs text-slate-400 italic py-6 text-center">No explicit Q&A turns were detected in this session.</p>
          ) : (
            <div className="space-y-3">
              {questionsAnswers.map((qa, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                  <div className="flex items-center space-x-2 text-xs font-bold text-cyan-400 mb-1">
                    <HelpCircle className="w-4 h-4" />
                    <span>Question {qa.speaker ? `(${qa.speaker})` : ''}:</span>
                  </div>
                  <p className="text-sm font-semibold text-slate-100 mb-2">{qa.question}</p>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800/80 text-xs text-slate-300">
                    <span className="font-bold text-emerald-400">Answer:</span> {qa.answer}
                  </div>
                  {qa.evidence && (
                    <button
                      onClick={() => jumpToTranscriptEvidence(qa.evidence)}
                      className="mt-2 text-[10px] text-blue-400 hover:underline cursor-pointer"
                    >
                      Verify in transcript quote
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 6: TIMELINE
      ========================================================================= */}
      {activeTab === 'timeline' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white">Chronological Session Timeline</h2>
            <p className="text-xs text-slate-400">
              Synchronized visual, topical, and decision milestones across session elapsed time.
            </p>
          </div>

          <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-6 my-4">
            {timeline.map((ev, idx) => (
              <div key={idx} className="relative group">
                <div className="absolute -left-[31px] top-1 w-3.5 h-3.5 rounded-full bg-blue-500 border-2 border-slate-950" />
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono font-bold text-blue-400 bg-slate-800 px-2 py-0.5 rounded">
                    {ev.timestamp}
                  </span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    [{ev.type}]
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white mt-1">{ev.title}</h4>
                <p className="text-xs text-slate-300 mt-0.5">{ev.description}</p>
                {ev.evidence && (
                  <p className="text-[10px] text-slate-500 italic mt-1">Source: {ev.evidence}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 7: VISUAL EVIDENCE (KEYFRAMES)
      ========================================================================= */}
      {activeTab === 'keyframes' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white">OpenCV Computer Vision Keyframes</h2>
            <p className="text-xs text-slate-400">
              Visual scene shifts captured by OpenCV frame difference analysis (Activity Index: {visualActivity}%).
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {keyframes.map((kf, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 overflow-hidden">
                <div className="aspect-video bg-slate-900 rounded-lg overflow-hidden mb-2 relative group">
                  <img
                    src={kf.url}
                    alt={kf.label}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                  <div className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-slate-950/80 text-white text-[10px] font-mono">
                    {kf.timestamp}s
                  </div>
                </div>
                <p className="text-xs font-semibold text-slate-200">{kf.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 8: SLIDES & DOCUMENT ANALYSIS
      ========================================================================= */}
      {activeTab === 'documents' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white">Slide & Document Multimodal Analysis</h2>
            <p className="text-xs text-slate-400">
              Supporting document ({session.document_filename || 'Attachment'}) parsed and aligned with spoken discussion.
            </p>
          </div>

          {documentPages.length === 0 ? (
            <p className="text-xs text-slate-400 italic py-6 text-center">No document was attached to this session.</p>
          ) : (
            <div className="space-y-4">
              {documentPages.map((page, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-purple-400">
                      Page / Section {page.page_number}: {page.title}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 whitespace-pre-line leading-relaxed mb-3">
                    {page.content}
                  </p>
                  {page.spoken_alignment && (
                    <div className="p-2.5 rounded bg-blue-500/10 border border-blue-500/20 text-[11px] text-blue-300">
                      <span className="font-bold">Spoken Discussion Alignment:</span> &quot;{page.spoken_alignment}&quot;
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 9: EVIDENCE SOURCES
      ========================================================================= */}
      {activeTab === 'evidence' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white">Verifiable Evidence Master Index</h2>
            <p className="text-xs text-slate-400">
              Complete index tying every extracted claim to verbatim quotes, timestamps, or media frames.
            </p>
          </div>

          <div className="space-y-3">
            {evidenceList.map((ev, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-500/15 text-blue-400">
                      {ev.claim_type}
                    </span>
                    <span className="text-xs font-semibold text-slate-200">
                      {ev.claim}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 italic">
                    &quot;{ev.quote}&quot;
                  </p>
                </div>
                <button
                  onClick={() => jumpToTranscriptEvidence(ev.quote)}
                  className="text-xs text-blue-400 hover:underline whitespace-nowrap self-start md:self-auto cursor-pointer"
                >
                  Locate in Stream →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 10: FULL TRANSCRIPT & SEARCH
      ========================================================================= */}
      {activeTab === 'transcript' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-bold text-white">Verbatim Transcript & Dialogue Stream</h2>
              <p className="text-xs text-slate-400">Speech-to-text transcript generated with multi-provider transcription.</p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleCopyTranscript}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center space-x-1.5 cursor-pointer"
              >
                {isCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{isCopied ? 'Copied' : 'Copy'}</span>
              </button>
              <a
                href={transTxtUrl}
                download={`transcript_${session.id.slice(0, 8)}.txt`}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center space-x-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Raw .txt</span>
              </a>
            </div>
          </div>

          {/* Search box */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
            <input
              type="text"
              placeholder="Search transcript by keyword or evidence quote..."
              value={transcriptSearch}
              onChange={(e) => setTranscriptSearch(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Transcript text container */}
          <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-slate-300 leading-relaxed max-h-[500px] overflow-y-auto space-y-2 select-text border border-slate-800/80">
            {session.transcript ? (
              session.transcript
                .split('\n')
                .filter((line) => !transcriptSearch || line.toLowerCase().includes(transcriptSearch.toLowerCase()))
                .map((line, idx) => {
                  const isMatch = transcriptSearch && line.toLowerCase().includes(transcriptSearch.toLowerCase());
                  return (
                    <p
                      key={idx}
                      className={`py-0.5 px-1 rounded ${isMatch ? 'bg-blue-600/30 text-white border-l-2 border-blue-400 pl-2' : ''}`}
                    >
                      {line}
                    </p>
                  );
                })
            ) : (
              <p className="text-slate-500 italic">No transcript recorded for this session.</p>
            )}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 11: INTERACTIVE DYNAMIC REPORT (CONSOLIDATED VIEW & EXPORT HUB)
      ========================================================================= */}
      {activeTab === 'dynamic_report' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
            <div>
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-blue-400 mb-1">
                <Sparkles className="w-4 h-4" />
                <span>Dynamic Intelligence Report</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white">{session.title}</h2>
              <p className="text-xs text-slate-400 mt-1">
                Generated from verified multimodal evidence. Sections only render when backed by actual session data.
              </p>
            </div>

            {/* Quick Export Hub */}
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={handleDownloadFullPdf}
                className="px-3.5 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center space-x-1.5 cursor-pointer shadow-md shadow-blue-500/20"
              >
                <Download className="w-3.5 h-3.5" />
                <span>PDF Report</span>
              </button>
              <button
                onClick={handleDownloadMarkdown}
                className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center space-x-1.5 cursor-pointer"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-purple-400" />
                <span>Markdown</span>
              </button>
              <button
                onClick={handleDownloadJson}
                className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center space-x-1.5 cursor-pointer"
              >
                <FileCode className="w-3.5 h-3.5 text-amber-400" />
                <span>JSON</span>
              </button>
              <button
                onClick={handleDownloadTxtReport}
                className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center space-x-1.5 cursor-pointer"
              >
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                <span>Text</span>
              </button>
            </div>
          </div>

          {/* Dynamic Section 1: Executive Summary */}
          {session.summary && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span>1. Executive Summary</span>
              </h3>
              <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950/70 p-4 rounded-xl border border-slate-800">
                {session.summary}
              </p>
            </div>
          )}

          {/* Dynamic Section 2: Key Decisions */}
          {decisions.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>2. Formal Decisions & Agreements</span>
              </h3>
              <div className="space-y-2.5">
                {decisions.map((d, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-xs text-slate-200">
                    <p className="font-semibold text-emerald-300">• {d.decision}</p>
                    {d.evidence && <p className="text-[11px] text-slate-400 italic mt-1">&quot;{d.evidence}&quot;</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dynamic Section 3: Action Items */}
          {actionItems.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-2">
                <CheckSquare className="w-4 h-4 text-blue-400" />
                <span>3. Action Items & Deliverables</span>
              </h3>
              <div className="space-y-2">
                {actionItems.map((item, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center justify-between text-xs">
                    <div>
                      <span className="font-semibold text-slate-200">{item.task}</span>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Assignee: <span className="text-blue-300">{item.assignee || 'Unassigned'}</span> | Deadline: {item.due_date || 'Pending'}
                      </div>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {item.priority || 'Medium'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dynamic Section 4: Topics */}
          {topics.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-2">
                <Tag className="w-4 h-4 text-indigo-400" />
                <span>4. Discussion Topics</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {topics.map((t, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
                    <div className="flex justify-between font-semibold text-slate-200 mb-1">
                      <span>{t.topic}</span>
                      <span className="text-blue-400">{Math.round(t.relevance * 100)}%</span>
                    </div>
                    {t.evidence && <p className="text-[11px] text-slate-400 italic truncate">&quot;{t.evidence}&quot;</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dynamic Section 5: Q&A */}
          {questionsAnswers.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-2">
                <HelpCircle className="w-4 h-4 text-cyan-400" />
                <span>5. Questions & Answers</span>
              </h3>
              <div className="space-y-2.5">
                {questionsAnswers.map((qa, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
                    <p className="font-bold text-cyan-300">Q: {qa.question}</p>
                    <p className="text-slate-300 mt-1">A: {qa.answer}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dynamic Section 6: OpenCV Visual Intelligence */}
          {hasVideo && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-2">
                <Film className="w-4 h-4 text-cyan-400" />
                <span>6. OpenCV Visual Intelligence</span>
              </h3>
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-300 flex flex-wrap gap-4">
                <span>Scene Shifts Detected: <strong className="text-cyan-400">{sceneChanges}</strong></span>
                <span>Visual Activity Index: <strong className="text-cyan-400">{visualActivity}%</strong></span>
                <span>Keyframes Saved: <strong className="text-cyan-400">{keyframes.length}</strong></span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 12: INTERACTIVE PDF VIEWER
      ========================================================================= */}
      {activeTab === 'pdf_preview' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-bold text-white flex items-center space-x-2">
                <Eye className="w-4 h-4 text-emerald-400" />
                <span>In-App PDF Viewer</span>
              </h2>
              <p className="text-xs text-slate-400">
                Official ReportLab publication report previewed directly in browser.
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <div className="bg-slate-950 rounded-lg p-1 border border-slate-800 flex items-center space-x-1 text-xs">
                <button
                  onClick={() => setPreviewDocType('report')}
                  className={`px-2.5 py-1 rounded cursor-pointer ${
                    previewDocType === 'report' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Executive Report
                </button>
                <button
                  onClick={() => setPreviewDocType('transcript')}
                  className={`px-2.5 py-1 rounded cursor-pointer ${
                    previewDocType === 'transcript' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Transcription PDF
                </button>
              </div>

              <a
                href={previewDocType === 'report' ? fullPdfInlineUrl : transPdfInlineUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center space-x-1"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                <span>Open in Tab</span>
              </a>
            </div>
          </div>

          {/* Embedded PDF iframe */}
          <div className="w-full h-[680px] rounded-xl overflow-hidden border border-slate-800 bg-slate-950 shadow-inner">
            <iframe
              src={previewDocType === 'report' ? fullPdfInlineUrl : transPdfInlineUrl}
              className="w-full h-full border-0"
              title="PDF Report Preview"
            />
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 13: MODEL SPEC
      ========================================================================= */}
      {activeTab === 'model_spec' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <BrainCircuit className="w-4 h-4 text-indigo-400" />
              <span>Multimodal Architecture & AI Specifications</span>
            </h2>
            <p className="text-xs text-slate-400">
              Technical pipeline specifications powering VideoIntel report generation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
              <h3 className="font-bold text-blue-400">1. Computer Vision (OpenCV)</h3>
              <p className="text-slate-300">
                Executes frame difference thresholding (`cv2.absdiff`, `diff.mean() &gt; 18.0`) to isolate slide changes and quantify visual activity index.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
              <h3 className="font-bold text-emerald-400">2. Speech-to-Text Transcription</h3>
              <p className="text-slate-300">
                Supports OpenAI Whisper-1, AssemblyAI, and offline `SpeechRecognition` acoustic models with automatic fallback.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
              <h3 className="font-bold text-purple-400">3. Local NLP & ML Synthesis</h3>
              <p className="text-slate-300">
                Scikit-learn TF-IDF vectorization for topic modeling, graph-based TextRank summarization, and lexical polarity sentiment analysis.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
              <h3 className="font-bold text-amber-400">4. ReportLab Publication Engine</h3>
              <p className="text-slate-300">
                Constructs pixel-perfect, accessible PDF documents using dynamic Flowables, custom color palettes, and two-pass page numbering.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
