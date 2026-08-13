import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FileText, Upload, Star, Sparkles, Plus, Trash2,
  X, BarChart3, Info, FileText as FileTextIcon,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { cvService, jobService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, LoadingSpinner, EmptyState, Modal, Badge } from '../components/ui';
import { formatDate, getScoreColor } from '../lib/utils';
import type { CV, CVList, JobOpportunity } from '../types';

type TabKey = 'content' | 'metadata' | 'analysis';

export default function CVManager() {
  const queryClient = useQueryClient();
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [selectedCV, setSelectedCV] = useState<CVList | null>(null);
  const [detailCV, setDetailCV] = useState<CV | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>('content');
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generatingCV, setGeneratingCV] = useState<number | null>(null);
  const [selectedJob, setSelectedJob] = useState<number | null>(null);
  const uploadInputRef = useState<HTMLInputElement | null>(null);

  const { data: cvs, isLoading: cvsLoading } = useQuery({
    queryKey: ['cvs'],
    queryFn: () => cvService.list({ limit: 100 }),
  });

  const { data: jobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['jobs', 'list'],
    queryFn: () => jobService.list({ limit: 50, status: 'open' }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => cvService.delete(id),
    onSuccess: () => {
      toast.success('CV deleted');
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
    },
    onError: () => toast.error('Failed to delete CV'),
  });

  const masterMutation = useMutation({
    mutationFn: (id: number) => cvService.setMaster(id),
    onSuccess: () => {
      toast.success('Master CV updated');
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
    },
  });

  const generateMutation = useMutation({
    mutationFn: ({ cvId, jobId }: { cvId: number; jobId: number }) =>
      cvService.generate({ cv_id: cvId, job_id: jobId }),
    onSuccess: () => {
      toast.success('Tailored CV generated!');
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
      setShowGenerateModal(false);
      setGeneratingCV(null);
      setSelectedJob(null);
    },
    onError: () => {
      toast.error('Generation failed');
      setGeneratingCV(null);
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: (id: number) => cvService.analyze(id),
    onSuccess: async (data, cvId) => {
      toast.success('CV analysis complete');
      setAnalysisResult(data);
      // Fetch full CV data to get updated AI fields AND update the selected CV in details modal
      try {
        const fullCV = await cvService.get(cvId);
        setDetailCV(fullCV);
        // Also update the selectedCV so the title etc. is fresh
        setSelectedCV(fullCV as any);
      } catch {
        // Ignore fetch error, analysis result is already shown
      }
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
    },
    onError: (error: Error) => {
      toast.error(`Analysis failed: ${error.message || 'Unknown error'}`);
    },
  });

  const handleUpload = async () => {
    if (!uploadFile) return;
    try {
      await cvService.upload(uploadFile, uploadFile.name);
      toast.success('CV uploaded');
      setUploadFile(null);
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
    } catch {
      toast.error('Upload failed');
    }
  };

  const handleGenerate = (cvId: number) => {
    setGeneratingCV(cvId);
    setShowGenerateModal(true);
  };

  const handleGenerateSubmit = () => {
    if (!generatingCV || !selectedJob) {
      toast.error('Please select a job');
      return;
    }
    generateMutation.mutate({ cvId: generatingCV, jobId: selectedJob });
  };

  const handleAnalyze = async (id: number) => {
    // Find the CV from the list to ensure we have it selected
    const cvToAnalyze = cvs?.find(c => c.id === id);
    if (cvToAnalyze) {
      setSelectedCV(cvToAnalyze);
      setShowDetails(true);
    }
    analyzeMutation.mutate(id);
    // Switch to analysis tab
    setActiveTab('analysis');
  };

  const handleViewCV = async (cv: CVList) => {
    setSelectedCV(cv);
    setActiveTab('content');
    setAnalysisResult(null);
    // Fetch full CV data for detailed view
    try {
      const fullCV = await cvService.get(cv.id);
      setDetailCV(fullCV);
    } catch (error) {
      console.error('Failed to fetch CV details:', error);
      toast.error('Failed to load CV details');
      setDetailCV(null);
    }
    setShowDetails(true);
  };

  const triggerUploadClick = () => {
    uploadInputRef.current?.click();
  };

  if (cvsLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My CVs</h1>
          <p className="text-sm text-gray-500 mt-1">Manage your master CV and tailored versions</p>
        </div>
        <div className="flex gap-2">
          <label className="flex items-center gap-2 px-4 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 cursor-pointer">
            <Upload className="w-4 h-4" />
            Upload CV
            <input
              type="file"
              accept=".pdf,.docx,.doc"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && setUploadFile(e.target.files[0])}
            />
          </label>
          {uploadFile && (
            <Button onClick={handleUpload} loading={false}>
              <Plus className="w-4 h-4" /> Add {uploadFile.name}
            </Button>
          )}
        </div>
      </div>

      {cvs && cvs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cvs.map((cv) => (
            <CVCard
              key={cv.id}
              cv={cv}
              onDelete={() => deleteMutation.mutate(cv.id)}
              onSetMaster={() => masterMutation.mutate(cv.id)}
              onGenerate={() => handleGenerate(cv.id)}
              onAnalyze={() => handleAnalyze(cv.id)}
              onClick={() => handleViewCV(cv)}
            />
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<FileText className="w-12 h-12" />}
            title="No CVs yet"
            description="Upload your master CV or create a tailored version for a specific job."
            action={
              <Button onClick={triggerUploadClick}>Upload First CV</Button>
            }
          />
        </Card>
      )}

      {/* Hidden file input */}
      <input
        ref={(el) => uploadInputRef.current = el}
        type="file"
        accept=".pdf,.docx,.doc"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && setUploadFile(e.target.files[0])}
      />

      {/* CV Details Modal */}
      <Modal isOpen={showDetails} onClose={() => setShowDetails(false)} title={selectedCV?.title || 'CV Details'} size="xl">
        {selectedCV && (
          <div className="space-y-4">
            {/* Tabs */}
            <div className="flex border-b border-gray-200">
              <TabButton
                active={activeTab === 'content'}
                onClick={() => setActiveTab('content')}
                icon={<FileTextIcon className="w-4 h-4" />}
                label="Content"
              />
              <TabButton
                active={activeTab === 'metadata'}
                onClick={() => setActiveTab('metadata')}
                icon={<Info className="w-4 h-4" />}
                label="Metadata"
              />
              <TabButton
                active={activeTab === 'analysis'}
                onClick={() => setActiveTab('analysis')}
                icon={<BarChart3 className="w-4 h-4" />}
                label="Analysis"
              />
            </div>

            {/* Content Tab */}
            {activeTab === 'content' && (
              <CVContentTab cv={detailCV} listCV={selectedCV} />
            )}

            {/* Metadata Tab */}
            {activeTab === 'metadata' && (
              <CVMetadataTab cv={detailCV} listCV={selectedCV} />
            )}

            {/* Analysis Tab */}
            {activeTab === 'analysis' && (
              <CVAnalysisTab
                cv={detailCV}
                analysisResult={analysisResult}
                onAnalyze={() => handleAnalyze(selectedCV.id)}
                isAnalyzing={analyzeMutation.isPending}
              />
            )}
          </div>
        )}
      </Modal>

      {/* Generate Modal */}
      <Modal
        isOpen={showGenerateModal}
        onClose={() => { setShowGenerateModal(false); setGeneratingCV(null); setSelectedJob(null); }}
        title="Generate Tailored CV"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Select a job opportunity to generate a tailored CV. The AI will optimize your resume
            to match the job requirements and highlight relevant skills.
          </p>

          {jobsLoading ? (
            <div className="flex justify-center py-4"><LoadingSpinner size="sm" /></div>
          ) : jobs && jobs.length > 0 ? (
            <div className="max-h-64 overflow-y-auto space-y-2">
              {jobs.map((job) => (
                <label
                  key={job.id}
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedJob === job.id
                      ? 'border-brand-500 bg-brand-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="selectedJob"
                    value={job.id}
                    checked={selectedJob === job.id}
                    onChange={() => setSelectedJob(job.id)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{job.title}</p>
                    <p className="text-sm text-gray-500">{job.company || 'No company'}</p>
                    {job.location && (
                      <p className="text-xs text-gray-400 mt-1">{job.location}</p>
                    )}
                  </div>
                </label>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500">
              <span className="text-2xl">💼</span>
              <p className="text-sm mt-2">No job opportunities found</p>
              <p className="text-xs mt-1">Add a job first to generate a tailored CV</p>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => { setShowGenerateModal(false); setGeneratingCV(null); setSelectedJob(null); }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleGenerateSubmit}
              disabled={!selectedJob || generateMutation.isPending}
              loading={generateMutation.isPending}
            >
              Generate CV
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

// ============================================================
// Tab Button Component
// ============================================================
function TabButton({ active, onClick, icon, label }: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
        active
          ? 'border-brand-500 text-brand-600'
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

// ============================================================
// Content Tab - Shows CV content
// ============================================================
function CVContentTab({ cv, listCV }: { cv: CV | null; listCV: CVList }) {
  // Try to get parsed data from the full CV first, then fall back to listCV
  const parsedDataFromCV = cv?.ai_parsed_data;

  // Check if this is an AI-generated CV (has parsed data with structured sections)
  const isAIGenerated = !!(parsedDataFromCV && (
    parsedDataFromCV.professional_summary ||
    parsedDataFromCV.skills ||
    parsedDataFromCV.work_experience ||
    parsedDataFromCV.education
  ));

  // For uploaded but not yet analyzed CVs, check if there's just a score
  const hasOnlyScore = !!listCV.ai_score && !cv?.ai_parsed_data && !parsedDataFromCV;

  const contentText = cv?.content_text || null;

  // AI-generated or analyzed CV with structured data - show formatted sections
  if (isAIGenerated && parsedDataFromCV) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-4 h-4 text-purple-500" />
          <span className="text-sm font-medium text-purple-700">AI-Generated CV</span>
        </div>
        {parsedDataFromCV.professional_summary && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-1">Professional Summary</h4>
            <p className="text-sm text-gray-600 whitespace-pre-wrap">{parsedDataFromCV.professional_summary}</p>
          </div>
        )}
        {parsedDataFromCV.skills && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-1">Skills</h4>
            <div className="flex flex-wrap gap-1">
              {(parsedDataFromCV.skills as string[]).map((skill: string, i: number) => (
                <span key={i} className="px-2 py-1 bg-brand-50 text-brand-700 text-xs rounded-md">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
        {parsedDataFromCV.work_experience && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-1">Work Experience</h4>
            <div className="space-y-3">
              {(parsedDataFromCV.work_experience as any[]).map((exp: any, i: number) => (
                <div key={i} className="border-l-2 border-gray-200 pl-3">
                  <p className="text-sm font-medium text-gray-800">{exp.position || exp.title || `Experience ${i + 1}`}</p>
                  <p className="text-xs text-gray-500">{exp.company}{exp.location ? ` • ${exp.location}` : ''}{exp.start ? ` • ${exp.start}${exp.end ? ` - ${exp.end}` : ''}` : ''}</p>
                  {exp.description && <p className="text-sm text-gray-600 mt-1 whitespace-pre-wrap">{exp.description}</p>}
                </div>
              ))}
            </div>
          </div>
        )}
        {parsedDataFromCV.education && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-1">Education</h4>
            <div className="space-y-2">
              {(parsedDataFromCV.education as any[]).map((edu: any, i: number) => (
                <div key={i} className="border-l-2 border-gray-200 pl-3">
                  <p className="text-sm font-medium text-gray-800">{edu.degree}{edu.field ? ` in ${edu.field}` : ''}</p>
                  <p className="text-xs text-gray-500">{edu.institution}{edu.start ? ` • ${edu.start}${edu.end ? ` - ${edu.end}` : ''}` : ''}</p>
                </div>
              ))}
            </div>
          </div>
        )}
        {parsedDataFromCV.certifications && Array.isArray(parsedDataFromCV.certifications) && parsedDataFromCV.certifications.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-1">Certifications</h4>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              {(parsedDataFromCV.certifications as string[]).map((cert: string, i: number) => (
                <li key={i}>{cert}</li>
              ))}
            </ul>
          </div>
        )}
        {parsedDataFromCV.key_achievements && Array.isArray(parsedDataFromCV.key_achievements) && parsedDataFromCV.key_achievements.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-1">Key Achievements</h4>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              {(parsedDataFromCV.key_achievements as string[]).map((achievement: string, i: number) => (
                <li key={i}>{achievement}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  // Uploaded CV with extracted text content
  if (contentText) {
    return (
      <div>
        <div className="flex items-center gap-2 mb-4">
          <FileTextIcon className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-600">Extracted Text Content</span>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <pre className="text-sm text-gray-600 whitespace-pre-wrap font-sans overflow-auto max-h-96">{contentText}</pre>
        </div>
      </div>
    );
  }

  // CV with only score (analyzed but no structured data) - show raw content text if available
  if (hasOnlyScore && contentText) {
    return (
      <div>
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-green-500" />
          <span className="text-sm font-medium text-green-700">Analyzed CV (Score: {listCV.ai_score}/100)</span>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <pre className="text-sm text-gray-600 whitespace-pre-wrap font-sans overflow-auto max-h-96">{contentText}</pre>
        </div>
      </div>
    );
  }

  // No content available
  return (
    <div className="text-center py-8">
      <FileTextIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
      <p className="text-sm text-gray-500">No content available for this CV</p>
      <p className="text-xs text-gray-400 mt-1">Try uploading a PDF/DOCX file or analyzing the CV</p>
    </div>
  );
}

// ============================================================
// Metadata Tab - Shows CV metadata
// ============================================================
function CVMetadataTab({ cv, listCV }: { cv: CV | null; listCV: CVList }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <MetadataItem label="CV ID" value={String(listCV.id)} />
        <MetadataItem label="Created" value={formatDate(listCV.created_at)} />
        <MetadataItem label="Updated" value={formatDate(cv?.updated_at || listCV.created_at)} />
        <MetadataItem label="Version" value={cv?.version || 'N/A'} />
        <MetadataItem label="Status">
          <div className="flex gap-2">
            {listCV.is_master && (
              <Badge color="bg-yellow-100 text-yellow-800">
                <Star className="w-3 h-3 mr-1" /> Master
              </Badge>
            )}
            {(listCV as any).is_ai_generated || cv?.is_ai_generated ? (
              <Badge color="bg-purple-100 text-purple-800">
                <Sparkles className="w-3 h-3 mr-1" /> AI Generated
              </Badge>
            ) : null}
            {!listCV.is_master && !(cv?.is_ai_generated) && <span className="text-sm text-gray-500">Regular CV</span>}
          </div>
        </MetadataItem>
        <MetadataItem label="AI Score" value={listCV.ai_score ? `${listCV.ai_score}/100` : 'Not analyzed'} />
      </div>

      {cv?.description && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-1">Description</h4>
          <p className="text-sm text-gray-600">{cv.description}</p>
        </div>
      )}

      {/* File Information */}
      {cv?.file_name && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">File Information</h4>
          <div className="grid grid-cols-2 gap-4">
            <MetadataItem label="File Name" value={cv.file_name} />
            <MetadataItem label="File Type" value={(cv.file_type || '').toUpperCase()} />
            <MetadataItem label="File Size" value={cv.file_size ? `${(cv.file_size / 1024).toFixed(1)} KB` : 'N/A'} />
            <MetadataItem label="Uploaded" value={cv.uploaded_at ? formatDate(cv.uploaded_at) : 'N/A'} />
          </div>
        </div>
      )}

      {/* Target Job Information (for tailored CVs) */}
      {cv?.target_job_title && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Target Job</h4>
          <div className="grid grid-cols-2 gap-4">
            <MetadataItem label="Job Title" value={cv.target_job_title} />
            <MetadataItem label="Company" value={cv.target_company || 'N/A'} />
            <MetadataItem label="Industry" value={cv.target_industry || 'N/A'} />
          </div>
        </div>
      )}

      {/* Career Profile */}
      {cv?.career_profile_id && (
        <div className="border-t pt-4">
          <MetadataItem label="Career Profile ID" value={String(cv.career_profile_id)} />
        </div>
      )}

      {/* Keywords */}
      {cv?.ai_keywords && cv.ai_keywords.length > 0 && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Keywords</h4>
          <div className="flex flex-wrap gap-1">
            {cv.ai_keywords.map((keyword: string, i: number) => (
              <span key={i} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================
// Analysis Tab - Shows AI analysis results
// ============================================================
function CVAnalysisTab({ cv, analysisResult, onAnalyze, isAnalyzing }: {
  cv: CV | null;
  analysisResult: any;
  onAnalyze: () => void;
  isAnalyzing: boolean;
}) {
  // Use the analysis result from the mutation, or fall back to CV data
  const result = analysisResult || null;
  const hasScore = cv?.ai_score != null;

  if (result) {
    return (
      <div className="space-y-4">
        {/* Overall Score */}
        <div className="flex items-center justify-center py-4">
          <div className="text-center">
            <div className={`text-5xl font-bold ${getScoreColor(result.overall_score || cv?.ai_score || 0)}`}>
              {result.overall_score || cv?.ai_score || 0}
            </div>
            <p className="text-sm text-gray-500 mt-2">Overall Score</p>
          </div>
        </div>

        {/* Dimension Scores */}
        {result.dimensions && Object.keys(result.dimensions).length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Dimension Scores</h4>
            <div className="space-y-3">
              {Object.entries(result.dimensions).map(([key, value]: [string, any]) => (
                <div key={key}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{key.replace(/_/g, ' ').replace(/\b\w/g (l) => l.toUpperCase())}</span>
                    <span className="font-medium text-gray-900">{typeof value === 'number' ? `${value}/10` : String(value)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all"
                      style={{
                        width: `${(typeof value === 'number' ? value : 0) * 10}%`,
                        backgroundColor: (typeof value === 'number' ? value : 0) * 10 >= 80 ? '#16a34a'
                          : (typeof value === 'number' ? value : 0) * 10 >= 60 ? '#ca8a04'
                          : (typeof value === 'number' ? value : 0) * 10 >= 40 ? '#ea580c'
                          : '#dc2626',
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Strengths */}
        {result.strengths && result.strengths.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-green-700 mb-2">Strengths</h4>
            <ul className="list-disc list-inside space-y-1">
              {(result.strengths as string[]).map((s: string, i: number) => (
                <li key={i} className="text-sm text-gray-700">{s}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Weaknesses */}
        {result.weaknesses && result.weaknesses.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-red-700 mb-2">Areas for Improvement</h4>
            <ul className="list-disc list-inside space-y-1">
              {(result.weaknesses as string[]).map((w: string, i: number) => (
                <li key={i} className="text-sm text-gray-700">{w}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Suggestions */}
        {result.suggestions && result.suggestions.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-blue-700 mb-2">Suggestions</h4>
            <ul className="list-disc list-inside space-y-1">
              {(result.suggestions as string[]).map((s: string, i: number) => (
                <li key={i} className="text-sm text-gray-700">{s}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Keywords */}
        {result.keywords && result.keywords.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Keywords</h4>
            <div className="flex flex-wrap gap-1">
              {(result.keywords as string[]).map((keyword: string, i: number) => (
                <span key={i} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  if (hasScore && cv?.ai_summary) {
    // Has score stored in DB but no fresh result
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-center py-4">
          <div className="text-center">
            <div className={`text-5xl font-bold ${getScoreColor(cv.ai_score)}`}>
              {cv.ai_score}
            </div>
            <p className="text-sm text-gray-500 mt-2">Overall Score</p>
          </div>
        </div>
        {cv.ai_keywords && cv.ai_keywords.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Keywords</h4>
            <div className="flex flex-wrap gap-1">
              {cv.ai_keywords.map((keyword: string, i: number) => (
                <span key={i} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}
        {cv.ai_summary && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Summary</h4>
            <p className="text-sm text-gray-600 whitespace-pre-wrap">{cv.ai_summary}</p>
          </div>
        )}
      </div>
    );
  }

  // No analysis yet
  return (
    <div className="text-center py-8">
      <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
      <p className="text-sm text-gray-500">This CV has not been analyzed yet</p>
      <p className="text-xs text-gray-400 mt-1">Click the button below to get AI-powered feedback</p>
      <Button
        className="mt-4"
        onClick={onAnalyze}
        loading={isAnalyzing}
        disabled={isAnalyzing}
      >
        <BarChart3 className="w-4 h-4 mr-2" />
        {isAnalyzing ? 'Analyzing...' : 'Analyze CV'}
      </Button>
    </div>
  );
}

// ============================================================
// CV Card Component
// ============================================================
function CVCard({
  cv,
  onDelete,
  onSetMaster,
  onGenerate,
  onAnalyze,
  onClick,
}: {
  cv: CVList;
  onDelete: () => void;
  onSetMaster: () => void;
  onGenerate: (cvId: number) => void;
  onAnalyze: (cvId: number) => void;
  onClick: () => void;
}) {
  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-brand-100 flex items-center justify-center">
              <FileText className="w-5 h-5 text-brand-600" />
            </div>
            <div>
              <CardTitle className="text-base">{cv.title}</CardTitle>
              <p className="text-xs text-gray-500">{formatDate(cv.created_at)}</p>
            </div>
          </div>
          <div className="flex gap-1">
            {cv.is_master && (
              <Badge color="bg-yellow-100 text-yellow-800">
                <Star className="w-3 h-3 mr-1" /> Master
              </Badge>
            )}
            {(cv as any).is_ai_generated && (
              <Badge color="bg-purple-100 text-purple-800">
                <Sparkles className="w-3 h-3 mr-1" /> AI
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {cv.ai_score && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">AI Score</span>
            <span className={`font-bold ${getScoreColor(cv.ai_score)}`}>{cv.ai_score}/100</span>
          </div>
        )}
        <div className="flex gap-2 flex-wrap">
          {!cv.is_master && (
            <Button variant="outline" size="sm" onClick={(e) => { e.stopPropagation(); onSetMaster(); }}>
              Set Master
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={(e) => { e.stopPropagation(); onAnalyze(cv.id); }}>
            Analyze
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => { e.stopPropagation(); onGenerate(cv.id); }}
          >
            <Sparkles className="w-3 h-3" /> Generate
          </Button>
          <Button variant="outline" size="sm" onClick={(e) => { e.stopPropagation(); onDelete(); }}>
            <Trash2 className="w-3 h-3 text-red-500" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================================
// Metadata Item Helper
// ============================================================
function MetadataItem({ label, value }: { label: string; value?: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs text-gray-500 mb-0.5">{label}</p>
      <p className="text-sm text-gray-900">{value || 'N/A'}</p>
    </div>
  );
}
