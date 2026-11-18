import React from 'react';
import { Video, History, PlayCircle, PlusCircle } from 'lucide-react';

interface NavbarProps {
  activeTab: 'new' | 'history' | 'result';
  setActiveTab: (tab: 'new' | 'history' | 'result') => void;
  onRunDemo: () => void;
  isProcessing: boolean;
  backendStatus: 'connecting' | 'healthy' | 'offline';
  historyCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onRunDemo,
  isProcessing,
  backendStatus,
  historyCount,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Branding */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('new')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 p-0.5 shadow-lg shadow-blue-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Video className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">MeetingMind</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                PBL AI Core
              </span>
            </div>
            <p className="text-xs text-slate-400">Multimodal Meeting Intelligence & Report Generator</p>
          </div>
        </div>

        {/* Center: Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-900/90 border border-slate-800 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('new')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'new'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Analysis</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'history'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Saved Sessions ({historyCount})</span>
          </button>
        </nav>

        {/* Right: Quick Action & Health Indicator */}
        <div className="flex items-center space-x-3">
          {/* Backend Health Badge */}
          <div className="hidden sm:flex items-center space-x-1.5 text-xs px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === 'healthy'
                  ? 'bg-emerald-500 animate-pulse'
                  : backendStatus === 'connecting'
                  ? 'bg-amber-400 animate-pulse'
                  : 'bg-rose-500'
              }`}
            />
            <span className="text-slate-400 text-[11px]">
              {backendStatus === 'healthy'
                ? 'Backend & SQLite Ready'
                : backendStatus === 'connecting'
                ? 'Connecting API...'
                : 'Backend Offline'}
            </span>
          </div>

          {/* Instant Faculty Demo Button */}
          <button
            onClick={onRunDemo}
            disabled={isProcessing}
            title="Runs real multimodal analysis on bundled sample meeting dataset"
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-md shadow-amber-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlayCircle className="w-4 h-4" />
            <span>Run Faculty Demo</span>
          </button>
        </div>
      </div>
    </header>
  );
};
