import React from 'react';
import {
  Download,
  FileText,
  Trash2,
  Clock,
  Calendar,
  Layers,
  ArrowRight,
} from 'lucide-react';
import type { MeetingSession } from '../types';
import { getPdfDownloadUrl, getDocxDownloadUrl, downloadFileBlob } from '../api';

interface SessionsHistoryProps {
  sessions: MeetingSession[];
  onSelectSession: (session: MeetingSession) => void;
  onDeleteSession: (id: string) => void;
  onNewAnalysis: () => void;
}

export const SessionsHistory: React.FC<SessionsHistoryProps> = ({
  sessions,
  onSelectSession,
  onDeleteSession,
  onNewAnalysis,
}) => {
  const handleDownloadPdf = async (sess: MeetingSession) => {
    try {
      await downloadFileBlob(getPdfDownloadUrl(sess.id), `VideoIntel_Executive_Report_${sess.id}.pdf`);
    } catch {
      window.location.href = getPdfDownloadUrl(sess.id);
    }
  };

  const handleDownloadDocx = async (sess: MeetingSession) => {
    try {
      await downloadFileBlob(getDocxDownloadUrl(sess.id), `Meeting_Intelligence_${sess.id.slice(0, 8)}.docx`);
    } catch {
      window.location.href = getDocxDownloadUrl(sess.id);
    }
  };
  const formatDuration = (secs: number) => {
    if (!secs) return 'N/A';
    const mins = Math.floor(secs / 60);
    const remainder = Math.floor(secs % 60);
    return `${mins}m ${remainder}s`;
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Saved Meeting Knowledge Reports</h1>
          <p className="text-xs text-slate-400 mt-1">
            Persisted in SQLite database. View past intelligence reports or download official PDF summaries.
          </p>
        </div>
        <button
          onClick={onNewAnalysis}
          className="px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-500/20 transition-all cursor-pointer"
        >
          + New Analysis
        </button>
      </div>

      {sessions.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center shadow-xl">
          <div className="w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-400 mx-auto mb-3">
            <Layers className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-white">No Saved Sessions Found</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Run an analysis on a video/audio file or click &apos;Run Faculty Demo&apos; to generate your first multimodal report.
          </p>
          <button
            onClick={onNewAnalysis}
            className="mt-4 px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200"
          >
            Start First Analysis
          </button>
        </div>
      ) : (
        <div className="space-y-3.5">
          {sessions.map((sess) => (
            <div
              key={sess.id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all shadow-md"
            >
              <div
                className="flex-1 min-w-0 cursor-pointer"
                onClick={() => onSelectSession(sess)}
              >
                <div className="flex flex-wrap items-center gap-2 mb-1.5">
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/25">
                    {sess.ai_provider || 'AI Engine'}
                  </span>
                  <span className="text-[10px] text-slate-400 flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{sess.created_at?.slice(0, 10) || 'Today'}</span>
                  </span>
                  {sess.duration_seconds > 0 && (
                    <span className="text-[10px] text-slate-400 flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{formatDuration(sess.duration_seconds)}</span>
                    </span>
                  )}
                </div>
                <h3 className="text-sm font-bold text-white truncate hover:text-blue-400 transition-colors">
                  {sess.title}
                </h3>
                <p className="text-xs text-slate-400 line-clamp-1 mt-1">
                  {sess.summary || 'Summary generated from multimodal audio & video data.'}
                </p>
              </div>

              <div className="flex items-center space-x-2 flex-shrink-0">
                <button
                  onClick={() => handleDownloadDocx(sess)}
                  className="p-2 rounded-lg bg-indigo-900/40 hover:bg-indigo-800 text-indigo-300 hover:text-white transition-colors cursor-pointer"
                  title="Download Word Report (.docx)"
                >
                  <FileText className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDownloadPdf(sess)}
                  className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors cursor-pointer"
                  title="Download PDF"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={() => onSelectSession(sess)}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 transition-colors"
                >
                  <span>View</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => onDeleteSession(sess.id)}
                  className="p-2 rounded-lg hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                  title="Delete Session"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
