import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Briefcase, MapPin, DollarSign, ExternalLink, Trash2, Edit2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { jobService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Textarea, LoadingSpinner, EmptyState, Modal, Badge } from '../components/ui';
import { formatDate, getStatusColor, humanize } from '../lib/utils';
import type { JobOpportunity } from '../types';

const JOB_TYPES = ['full_time', 'part_time', 'contract', 'internship', 'freelance', 'temporary'];
const JOB_STATUSES = ['open', 'closed', 'archived'];

export default function JobOpportunities() {
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<JobOpportunity | null>(null);
  const [form, setForm] = useState<any>({
    title: '', company: '', location: '', job_type: 'full_time',
    is_remote: false, salary_min: '', salary_max: '', salary_currency: 'USD',
    description: '', requirements: '', responsibilities: '', benefits: '',
    source: '', source_url: '', status: 'open', deadline: '',
  });

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobService.list({ limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => jobService.create(data),
    onSuccess: () => {
      toast.success('Job opportunity created');
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setIsOpen(false);
      resetForm();
    },
    onError: () => toast.error('Failed to create job'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => jobService.update(id, data),
    onSuccess: () => {
      toast.success('Job updated');
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setIsOpen(false);
      setEditing(null);
    },
    onError: () => toast.error('Failed to update job'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => jobService.delete(id),
    onSuccess: () => {
      toast.success('Job deleted');
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
    onError: () => toast.error('Failed to delete job'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      salary_min: form.salary_min ? parseInt(form.salary_min) : null,
      salary_max: form.salary_max ? parseInt(form.salary_max) : null,
      is_remote: form.is_remote ? 1 : 0,  // Convert boolean to integer for backend
    };
    if (editing) {
      updateMutation.mutate({ id: editing.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const resetForm = () => {
    setForm({
      title: '', company: '', location: '', job_type: 'full_time',
      is_remote: false, salary_min: '', salary_max: '', salary_currency: 'USD',
      description: '', requirements: '', responsibilities: '', benefits: '',
      source: '', source_url: '', status: 'open', deadline: '',
    });
  };

  const openEdit = (job: JobOpportunity) => {
    setEditing(job);
    setForm({
      ...job,
      salary_min: job.salary_min || '',
      salary_max: job.salary_max || '',
      deadline: job.deadline ? new Date(job.deadline).toISOString().split('T')[0] : '',
    });
    setIsOpen(true);
  };

  const openCreate = () => {
    setEditing(null);
    resetForm();
    setIsOpen(true);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Job Opportunities</h1>
          <p className="text-sm text-gray-500 mt-1">Track and manage your target positions</p>
        </div>
        <Button onClick={openCreate}><Plus className="w-4 h-4" /> Add Job</Button>
      </div>

      {jobs && jobs.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {jobs.map((job) => (
            <Card key={job.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{job.title}</CardTitle>
                    <p className="text-sm text-gray-500 mt-1">{job.company || 'No company'}</p>
                  </div>
                  <Badge color={getStatusColor(job.status)}>{humanize(job.status)}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-2 text-sm text-gray-500">
                  {job.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {job.location}</span>}
                  {job.salary_min && (
                    <span className="flex items-center gap-1"><DollarSign className="w-3 h-3" />
                      {job.salary_min.toLocaleString()} - {job.salary_max?.toLocaleString()} {job.salary_currency}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 line-clamp-2">{job.description}</p>
                <div className="flex items-center justify-between pt-2">
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => openEdit(job)}><Edit2 className="w-3 h-3" /></Button>
                    <Button variant="outline" size="sm" onClick={() => deleteMutation.mutate(job.id)}><Trash2 className="w-3 h-3 text-red-500" /></Button>
                  </div>
                  {job.source_url && (
                    <a href={job.source_url} target="_blank" rel="noopener noreferrer" className="text-sm text-brand-600 hover:underline flex items-center gap-1">
                      View <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<Briefcase className="w-12 h-12" />}
            title="No job opportunities yet"
            description="Start tracking the jobs you're interested in."
            action={<Button onClick={openCreate}><Plus className="w-4 h-4" /> Add First Job</Button>}
          />
        </Card>
      )}

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title={editing ? 'Edit Job' : 'Add Job'} size="lg">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Title</Label>
              <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
            </div>
            <div>
              <Label>Company</Label>
              <Input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
            </div>
            <div>
              <Label>Location</Label>
              <Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
            </div>
            <div>
              <Label>Job Type</Label>
              <select
                value={form.job_type}
                onChange={(e) => setForm({ ...form, job_type: e.target.value })}
                className="w-full h-10 rounded-md border border-gray-300 px-3"
              >
                {JOB_TYPES.map((t) => <option key={t} value={t}>{humanize(t)}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>Min Salary</Label>
              <Input type="number" value={form.salary_min} onChange={(e) => setForm({ ...form, salary_min: e.target.value })} />
            </div>
            <div>
              <Label>Max Salary</Label>
              <Input type="number" value={form.salary_max} onChange={(e) => setForm({ ...form, salary_max: e.target.value })} />
            </div>
            <div>
              <Label>Currency</Label>
              <Input value={form.salary_currency} onChange={(e) => setForm({ ...form, salary_currency: e.target.value })} />
            </div>
          </div>
          <div>
            <Label>Description</Label>
            <Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} />
          </div>
          <div>
            <Label>Requirements</Label>
            <Textarea value={form.requirements} onChange={(e) => setForm({ ...form, requirements: e.target.value })} rows={3} />
          </div>
          <div>
            <Label>Deadline</Label>
            <Input type="date" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsOpen(false)} type="button">Cancel</Button>
            <Button type="submit" loading={createMutation.isPending || updateMutation.isPending}>{editing ? 'Update' : 'Create'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

const Label = ({ children, htmlFor }: { children: React.ReactNode; htmlFor?: string }) => (
  <label htmlFor={htmlFor} className="block text-sm font-medium text-gray-700 mb-1.5">{children}</label>
);
