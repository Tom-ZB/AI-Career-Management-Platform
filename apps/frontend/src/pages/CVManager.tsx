import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FileText, Upload, Star, Sparkles, Plus, Trash2, Edit3,
  Briefcase, X,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { cvService, jobService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, LoadingSpinner, EmptyState, Modal, Badge } from '../components/ui';
import { formatDate, getScoreColor } from '../lib/utils';
import type { CVList, JobOpportunity } from '../types';

export default function CVManager() {
  const queryClient = useQueryClient();
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [selectedCV, setSelectedCV] = useState<CVList | null>(null);
  const [showDetails, setShowDetails] = useState(false);
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
    try {
      await cvService.analyze(id);
      toast.success('CV analysis complete');
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
    } catch {
      toast.error('Analysis failed');
    }
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
              onClick={() => { setSelectedCV(cv); setShowDetails(true); }}
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

      {/* Details Modal */}
      <Modal isOpen={showDetails} onClose={() => setShowDetails(false)} title="CV Details" size="lg">
        {selectedCV && (
          <div className="space-y-4">
            <p className="text-sm text-gray-500">ID: {selectedCV.id}</p>
            <p className="text-sm text-gray-500">Created: {formatDate(selectedCV.created_at)}</p>
            <p className="text-sm text-gray-500">AI Score: {selectedCV.ai_score || 'N/A'}</p>
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
              <Briefcase className="w-8 h-8 mx-auto mb-2 text-gray-300" />
              <p className="text-sm">No job opportunities found</p>
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
          {cv.is_master && (
            <Badge color="bg-yellow-100 text-yellow-800">
              <Star className="w-3 h-3 mr-1" /> Master
            </Badge>
          )}
          {cv.is_ai_generated && (
            <Badge color="bg-purple-100 text-purple-800">
              <Sparkles className="w-3 h-3 mr-1" /> AI
            </Badge>
          )}
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
          <Button variant="outline" size="sm" onClick={(e) => { e.stopPropagation(); onAnalyze(); }}>
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
