// ============================================
// AI Career Management Platform - Types
// ============================================

// Auth
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  refresh_token?: string;
}

export interface LoginCredentials {
  username: string; // email
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

// Career Profile
export interface CareerProfile {
  id: number;
  user_id: number;
  full_name: string | null;
  title: string | null;
  summary: string | null;
  skills: string[] | null;
  experience_years: number | null;
  education: Education[] | null;
  work_experience: WorkExperience[] | null;
  contact_info: Record<string, any> | null;
  social_links: Record<string, string> | null;
  created_at: string;
  updated_at: string;
}

export interface Education {
  institution: string;
  degree: string;
  field: string;
  start: string;
  end: string;
}

export interface WorkExperience {
  company: string;
  position: string;
  start: string;
  end: string;
  description: string;
}

// CV
export interface CV {
  id: number;
  user_id: number;
  career_profile_id: number | null;
  title: string;
  version: string | null;
  description: string | null;
  is_master: boolean;
  is_public: boolean;
  is_ai_generated: boolean;
  target_job_title: string | null;
  target_company: string | null;
  file_name: string | null;
  file_type: string | null;
  ai_score: number | null;
  ai_summary: string | null;
  content_text: string | null;
  created_at: string;
  updated_at: string;
}

export interface CVList {
  id: number;
  title: string;
  is_master: boolean;
  is_ai_generated: boolean;
  ai_score: number | null;
  created_at: string;
}

// Job Opportunity
export type JobStatus = 'open' | 'closed' | 'archived';
export type JobType = 'full_time' | 'part_time' | 'contract' | 'internship' | 'freelance' | 'temporary';

export interface JobOpportunity {
  id: number;
  user_id: number;
  title: string;
  company: string | null;
  location: string | null;
  job_type: JobType;
  is_remote: boolean;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  description: string | null;
  requirements: string | null;
  source: string | null;
  source_url: string | null;
  status: JobStatus;
  deadline: string | null;
  created_at: string;
  updated_at: string;
}

// Job Application
export type ApplicationStatus =
  | 'draft' | 'applied' | 'screening' | 'interview'
  | 'offer' | 'accepted' | 'rejected' | 'withdrawn';

export interface JobApplication {
  id: number;
  user_id: number;
  job_opportunity_id: number;
  cv_id: number | null;
  status: ApplicationStatus;
  application_date: string | null;
  deadline: string | null;
  cover_letter_content: string | null;
  cover_letter_ai_generated: boolean;
  notes: string | null;
  referral_source: string | null;
  created_at: string;
  updated_at: string;
}

// Interview
export type InterviewType = 'phone' | 'video' | 'onsite' | 'technical' | 'behavioral' | 'case_study' | 'final_round';
export type InterviewStatus = 'scheduled' | 'completed' | 'cancelled' | 'rescheduled' | 'no_show';

export interface Interview {
  id: number;
  user_id: number;
  application_id: number;
  interview_type: InterviewType;
  title: string | null;
  description: string | null;
  location: string | null;
  meeting_url: string | null;
  scheduled_at: string;
  duration_minutes: number | null;
  interviewer_name: string | null;
  status: InterviewStatus;
  rating: number | null;
  feedback: string | null;
  created_at: string;
}

// Follow-up
export type FollowUpType = 'email' | 'phone_call' | 'message' | 'meeting' | 'thank_you' | 'follow_up_email' | 'networking';
export type FollowUpStatus = 'pending' | 'completed' | 'missed' | 'cancelled';

export interface FollowUp {
  id: number;
  user_id: number;
  application_id: number | null;
  follow_up_type: FollowUpType;
  title: string | null;
  priority: number;
  scheduled_at: string;
  status: FollowUpStatus;
  contact_person: string | null;
  completed_at: string | null;
  created_at: string;
}

// Document
export type DocumentType = 'cv' | 'cover_letter' | 'certificate' | 'transcript' | 'portfolio' | 'job_description' | 'other';

export interface Document {
  id: number;
  user_id: number;
  document_type: DocumentType;
  title: string | null;
  file_name: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  created_at: string;
}

// AI
export interface ChatMessage {
  id: number;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  processing_time_ms: number | null;
  model_used: string | null;
}

export interface MatchResult {
  match_id: number;
  cv_id: number;
  job_id: number;
  overall_score: number;
  skills_score: number;
  experience_score: number;
  education_score: number;
  keywords_score: number;
  strengths: string[];
  gaps: string[];
  recommendation: string;
  tips: string[];
}

export interface DashboardStats {
  applications: {
    total: number;
    by_status: Record<string, number>;
    trend: any[];
  };
  jobs: {
    total: number;
    by_type: Record<string, number>;
    by_source: Record<string, number>;
  };
  interviews: {
    total: number;
    upcoming: number;
    completed: number;
  };
  follow_ups: {
    total: number;
    pending: number;
    overdue: number;
  };
  match_rate: number;
  response_rate: number;
}

// API
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  message?: string;
}
