import apiClient from './api';
import type {
  CV, CVList, JobOpportunity, JobApplication, Interview, FollowUp,
  Document, MatchResult, ChatResponse, DashboardStats,
} from '../types';

// ============================================
// Career Profile
// ============================================
export const profileService = {
  async get(): Promise<any> {
    const response = await apiClient.get('/profiles/me');
    return response.data;
  },
  async create(data: any): Promise<any> {
    const response = await apiClient.post('/profiles/', data);
    return response.data;
  },
  async update(data: any): Promise<any> {
    const response = await apiClient.patch('/profiles/me', data);
    return response.data;
  },
};

// ============================================
// CVs
// ============================================
export const cvService = {
  async list(params?: { skip?: number; limit?: number; is_master?: boolean; search?: string }): Promise<CVList[]> {
    const response = await apiClient.get<CVList[]>('/cvs/', { params });
    return response.data;
  },
  async get(id: number): Promise<CV> {
    const response = await apiClient.get<CV>(`/cvs/${id}`);
    return response.data;
  },
  async create(data: any): Promise<CV> {
    const response = await apiClient.post<CV>('/cvs/', data);
    return response.data;
  },
  async update(id: number, data: any): Promise<CV> {
    const response = await apiClient.put<CV>(`/cvs/${id}`, data);
    return response.data;
  },
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/cvs/${id}`);
  },
  async setMaster(id: number): Promise<CV> {
    const response = await apiClient.post<CV>(`/cvs/${id}/set-master`);
    return response.data;
  },
  async analyze(id: number): Promise<any> {
    const response = await apiClient.post(`/cvs/${id}/analyze`);
    return response.data;
  },
  async generate(request: any): Promise<any> {
    const response = await apiClient.post('/cvs/generate', request);
    return response.data;
  },
  async upload(file: File, title?: string): Promise<CV> {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    const response = await apiClient.post<CV>('/cvs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

// ============================================
// Job Opportunities
// ============================================
export const jobService = {
  async list(params?: any): Promise<JobOpportunity[]> {
    const response = await apiClient.get<JobOpportunity[]>('/jobs/', { params });
    return response.data;
  },
  async get(id: number): Promise<JobOpportunity> {
    const response = await apiClient.get<JobOpportunity>(`/jobs/${id}`);
    return response.data;
  },
  async create(data: any): Promise<JobOpportunity> {
    const response = await apiClient.post<JobOpportunity>('/jobs/', data);
    return response.data;
  },
  async update(id: number, data: any): Promise<JobOpportunity> {
    const response = await apiClient.put<JobOpportunity>(`/jobs/${id}`, data);
    return response.data;
  },
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/jobs/${id}`);
  },
  async stats(): Promise<any> {
    const response = await apiClient.get('/jobs/stats');
    return response.data;
  },
};

// ============================================
// Job Applications
// ============================================
export const applicationService = {
  async list(params?: any): Promise<JobApplication[]> {
    const response = await apiClient.get<JobApplication[]>('/applications/', { params });
    return response.data;
  },
  async get(id: number): Promise<JobApplication> {
    const response = await apiClient.get<JobApplication>(`/applications/${id}`);
    return response.data;
  },
  async create(data: any): Promise<JobApplication> {
    const response = await apiClient.post<JobApplication>('/applications/', data);
    return response.data;
  },
  async update(id: number, data: any): Promise<JobApplication> {
    const response = await apiClient.put<JobApplication>(`/applications/${id}`, data);
    return response.data;
  },
  async updateStatus(id: number, status: string): Promise<JobApplication> {
    const response = await apiClient.put<JobApplication>(`/applications/${id}/status`, null, {
      params: { status },
    });
    return response.data;
  },
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/applications/${id}`);
  },
  async stats(): Promise<any> {
    const response = await apiClient.get('/applications/stats');
    return response.data;
  },
};

// ============================================
// Interviews
// ============================================
export const interviewService = {
  async list(params?: any): Promise<Interview[]> {
    const response = await apiClient.get<Interview[]>('/interviews/', { params });
    return response.data;
  },
  async get(id: number): Promise<Interview> {
    const response = await apiClient.get<Interview>(`/interviews/${id}`);
    return response.data;
  },
  async create(data: any): Promise<Interview> {
    const response = await apiClient.post<Interview>('/interviews/', data);
    return response.data;
  },
  async update(id: number, data: any): Promise<Interview> {
    const response = await apiClient.put<Interview>(`/interviews/${id}`, data);
    return response.data;
  },
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/interviews/${id}`);
  },
  async generatePrep(id: number): Promise<any> {
    const response = await apiClient.post(`/interviews/${id}/prep`);
    return response.data;
  },
};

// ============================================
// Follow-ups
// ============================================
export const followUpService = {
  async list(params?: any): Promise<FollowUp[]> {
    const response = await apiClient.get<FollowUp[]>('/follow-ups/', { params });
    return response.data;
  },
  async get(id: number): Promise<FollowUp> {
    const response = await apiClient.get<FollowUp>(`/follow-ups/${id}`);
    return response.data;
  },
  async create(data: any): Promise<FollowUp> {
    const response = await apiClient.post<FollowUp>('/follow-ups/', data);
    return response.data;
  },
  async update(id: number, data: any): Promise<FollowUp> {
    const response = await apiClient.put<FollowUp>(`/follow-ups/${id}`, data);
    return response.data;
  },
  async complete(id: number, outcome?: string): Promise<FollowUp> {
    const response = await apiClient.put<FollowUp>(`/follow-ups/${id}/complete`, null, {
      params: { outcome },
    });
    return response.data;
  },
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/follow-ups/${id}`);
  },
};

// ============================================
// Documents
// ============================================
export const documentService = {
  async list(params?: any): Promise<Document[]> {
    const response = await apiClient.get<Document[]>('/documents/', { params });
    return response.data;
  },
  async get(id: number): Promise<Document> {
    const response = await apiClient.get<Document>(`/documents/${id}`);
    return response.data;
  },
  async create(data: any): Promise<Document> {
    const response = await apiClient.post<Document>('/documents/', data);
    return response.data;
  },
  async update(id: number, data: any): Promise<Document> {
    const response = await apiClient.put<Document>(`/documents/${id}`, data);
    return response.data;
  },
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/documents/${id}`);
  },
  async upload(file: File, documentType?: string, title?: string): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    if (documentType) formData.append('document_type', documentType);
    if (title) formData.append('title', title);
    const response = await apiClient.post<Document>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

// ============================================
// AI Services
// ============================================
export const aiService = {
  async chat(message: string, sessionId?: string): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/ai/chat', {
      message,
      session_id: sessionId,
    });
    return response.data;
  },
  async analyzeCV(cvId: number): Promise<any> {
    const response = await apiClient.post(`/ai/analyze-cv/${cvId}`);
    return response.data;
  },
  async match(cvId: number, jobId: number): Promise<MatchResult> {
    const response = await apiClient.post<MatchResult>('/ai/match', { cv_id: cvId, job_id: jobId });
    return response.data;
  },
  async generateCV(jobId: number, profileId?: number): Promise<any> {
    const response = await apiClient.post('/ai/generate-cv', { job_id: jobId, profile_id: profileId });
    return response.data;
  },
  async generateCoverLetter(cvId: number, jobId: number): Promise<any> {
    const response = await apiClient.post('/ai/generate-cover-letter', { cv_id: cvId, job_id: jobId });
    return response.data;
  },
  async query(question: string): Promise<any> {
    const response = await apiClient.post('/ai/query', null, { params: { query: question } });
    return response.data;
  },
  async agentAction(actionType: string, params?: any): Promise<any> {
    const response = await apiClient.post('/ai/agent/action', params, {
      params: { action_type: actionType },
    });
    return response.data;
  },
};

// ============================================
// Analytics
// ============================================
export const analyticsService = {
  async dashboard(): Promise<DashboardStats> {
    const response = await apiClient.get<DashboardStats>('/analytics/dashboard');
    return response.data;
  },
  async applicationsTrend(period: string = '30d'): Promise<any> {
    const response = await apiClient.get('/analytics/applications/trend', { params: { period } });
    return response.data;
  },
  async applicationsByStatus(): Promise<any> {
    const response = await apiClient.get('/analytics/applications/by-status');
    return response.data;
  },
  async aiUsage(period: string = '30d'): Promise<any> {
    const response = await apiClient.get('/analytics/ai-usage', { params: { period } });
    return response.data;
  },
};

// ============================================
// Export
// ============================================
export const exportService = {
  async exportApplicationsPDF(status?: string): Promise<Blob> {
    const response = await apiClient.get('/export/applications/pdf', {
      params: { status },
      responseType: 'blob',
    });
    return response.data;
  },
  async exportApplicationsCSV(status?: string): Promise<Blob> {
    const response = await apiClient.get('/export/applications/csv', {
      params: { status },
      responseType: 'blob',
    });
    return response.data;
  },
};
