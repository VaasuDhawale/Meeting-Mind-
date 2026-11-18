export interface ActionItem {
  task: string;
  assignee?: string;
  priority?: 'High' | 'Medium' | 'Low' | string;
  due_date?: string;
  status?: 'pending' | 'completed' | string;
  evidence?: string;
  timestamp?: string | null;
}

export interface DecisionItem {
  decision: string;
  context?: string;
  participants?: string;
  timestamp?: string | null;
  evidence?: string;
}

export interface Topic {
  topic: string;
  relevance: number;
  keywords: string[];
  supporting_points?: string[];
  evidence?: string;
  timestamp?: string | null;
}

export interface QuestionAnswer {
  question: string;
  answer: string;
  speaker?: string | null;
  timestamp?: string | null;
  evidence?: string;
}

export interface TimelineEvent {
  timestamp: string;
  time_seconds: number;
  type: 'keyframe' | 'topic' | 'decision' | 'action' | 'slide' | string;
  title: string;
  description: string;
  evidence?: string;
}

export interface DocumentPage {
  page_number: number;
  title: string;
  content: string;
  spoken_alignment?: string | null;
  evidence?: string;
}

export interface DocumentAnalysis {
  document_name?: string;
  total_pages?: number;
  pages?: DocumentPage[];
  summary?: string;
}

export interface EvidenceItem {
  id: string;
  claim_type: 'decision' | 'action_item' | 'topic' | 'qa' | 'visual' | 'document' | string;
  claim: string;
  source_type: string;
  timestamp?: string | null;
  quote: string;
}

export interface SentimentAnalysis {
  overall: 'Positive' | 'Constructive' | 'Neutral' | string;
  positive_score: number;
  neutral_score: number;
  negative_score: number;
}

export interface VideoKeyframe {
  timestamp: number;
  url: string;
  label: string;
}

export interface VideoAnalysis {
  duration_seconds?: number;
  keyframes: VideoKeyframe[];
  scene_changes: number;
  visual_activity: number;
  fps?: number;
  resolution?: string;
}

export interface Speaker {
  name: string;
  speaking_time: number;
  percentage: number;
  turns?: number;
}

export interface MeetingSession {
  id: string;
  title: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string | null;
  created_at?: string;
  duration_seconds: number;
  source_filename?: string;
  source_file_type?: 'video' | 'audio' | string;
  document_filename?: string | null;
  ai_provider: string;
  transcript?: string;
  summary?: string;
  action_items: ActionItem[];
  decisions: (string | DecisionItem)[];
  topics: Topic[];
  sentiment: SentimentAnalysis;
  video_analysis: VideoAnalysis;
  speakers: Speaker[];
  questions_answers?: QuestionAnswer[];
  timeline?: TimelineEvent[];
  document_analysis?: DocumentAnalysis;
  evidence?: EvidenceItem[];
  has_pdf: boolean;
  has_docx?: boolean;
}
