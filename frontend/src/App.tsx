import { useState, useEffect, useRef } from 'react';
import { StorytellingLanding } from './components/StorytellingLanding';
import { Navbar } from './components/Navbar';
import { ProcessingOverlay } from './components/ProcessingOverlay';
import { ResultsView } from './components/ResultsView';
import { SessionsHistory } from './components/SessionsHistory';
import type { MeetingSession } from './types';
import {
  checkBackendHealth,
  getSessions,
  analyzeSession,
  runFacultyDemo,
  deleteSession,
} from './api';

export function App() {
  const [activeTab, setActiveTab] = useState<'new' | 'history' | 'result'>('new');
  const [selectedSession, setSelectedSession] = useState<MeetingSession | null>(null);
  const [sessions, setSessions] = useState<MeetingSession[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [backendStatus, setBackendStatus] = useState<'connecting' | 'healthy' | 'offline'>('connecting');
  const [globalError, setGlobalError] = useState<string | null>(null);

  const timerRef = useRef<number | null>(null);
  const stageTimerRef = useRef<number | null>(null);

  // Initial load: check health and retrieve historical sessions
  useEffect(() => {
    let isMounted = true;
    const fetchHealthAndSessions = async () => {
      const healthy = await checkBackendHealth();
      if (!isMounted) return;
      setBackendStatus(healthy ? 'healthy' : 'offline');
      if (healthy) {
        try {
          const list = await getSessions();
          if (isMounted) setSessions(list);
        } catch (err) {
          console.error('Failed to load sessions', err);
        }
      }
    };
    fetchHealthAndSessions();
    const interval = setInterval(fetchHealthAndSessions, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const startProgressTracking = () => {
    setIsProcessing(true);
    setProcessingStage(0);
    setElapsedSeconds(0);

    timerRef.current = window.setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);

    // Progression of pipeline steps: 0 -> 1 -> 2 -> 3 -> 4
    stageTimerRef.current = window.setInterval(() => {
      setProcessingStage((prev) => (prev < 4 ? prev + 1 : prev));
    }, 3500);
  };

  const stopProgressTracking = () => {
    setIsProcessing(false);
    if (timerRef.current) clearInterval(timerRef.current);
    if (stageTimerRef.current) clearInterval(stageTimerRef.current);
  };

  const handleAnalyze = async (formData: FormData) => {
    setGlobalError(null);
    startProgressTracking();
    try {
      const result = await analyzeSession(formData);
      setSelectedSession(result);
      setActiveTab('result');
      // Refresh sessions
      const list = await getSessions();
      setSessions(list);
    } catch (err: any) {
      console.error('Analysis error', err);
      const detail = err.response?.data?.detail || err.message || 'Analysis encountered an error';
      setGlobalError(`Processing failed: ${detail}`);
    } finally {
      stopProgressTracking();
    }
  };

  const handleRunDemo = async () => {
    setGlobalError(null);
    startProgressTracking();
    try {
      const result = await runFacultyDemo();
      setSelectedSession(result);
      setActiveTab('result');
      const list = await getSessions();
      setSessions(list);
    } catch (err: any) {
      console.error('Demo error', err);
      const detail = err.response?.data?.detail || err.message || 'Demo execution encountered an error';
      setGlobalError(`Demo execution failed: ${detail}`);
    } finally {
      stopProgressTracking();
    }
  };

  const handleSelectSession = (session: MeetingSession) => {
    setSelectedSession(session);
    setActiveTab('result');
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (selectedSession?.id === id) {
        setSelectedSession(null);
        setActiveTab('new');
      }
    } catch (err) {
      console.error('Delete error', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Global Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRunDemo={handleRunDemo}
        isProcessing={isProcessing}
        backendStatus={backendStatus}
        historyCount={sessions.length}
      />

      {/* Global Error Banner if any */}
      {globalError && (
        <div className="max-w-4xl mx-auto w-full px-4 pt-4">
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
            <span>{globalError}</span>
            <button
              onClick={() => setGlobalError(null)}
              className="text-rose-400 hover:text-rose-200 font-bold ml-4"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Main Content Areas */}
      <main className="flex-1">
        {activeTab === 'new' && (
          <StorytellingLanding
            onSubmit={handleAnalyze}
            onRunDemo={handleRunDemo}
            isProcessing={isProcessing}
          />
        )}

        {activeTab === 'result' && selectedSession && (
          <ResultsView
            session={selectedSession}
            onNewAnalysis={() => setActiveTab('new')}
          />
        )}

        {activeTab === 'history' && (
          <SessionsHistory
            sessions={sessions}
            onSelectSession={handleSelectSession}
            onDeleteSession={handleDeleteSession}
            onNewAnalysis={() => setActiveTab('new')}
          />
        )}
      </main>

      {/* Processing Animation Overlay */}
      {isProcessing && (
        <ProcessingOverlay
          currentStage={processingStage}
          elapsedSeconds={elapsedSeconds}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-400">
        <p>
          AI-Powered Meeting & Video Intelligence Report Generator • Final Year Project Evaluation
        </p>
      </footer>
    </div>
  );
}

export default App;
