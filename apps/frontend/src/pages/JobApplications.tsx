import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Send, Calendar, FileText, Edit2, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { applicationService, jobService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Textarea, LoadingSpinner, EmptyState, Modal, Badge } from '../components/ui';
import { formatDate, getStatusColor, humanize } from '../lib/utils';
import type { JobApplication } from '../types';

const STATUSES = ['draft', 'applied', 'screening', 'interview', 'offer', 'accepted', 'rejected', 'withdrawn'];

export default function JobApplications() {
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<JobApplication | null>(null);
  const [form, setForm] = useState<any>({
    job_opportunity_id: '', cv_id: '', status: 'applied',
    application_date: '', deadline: '', notes: '',
  });

  const { data: applications, isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationService.list({ limit: 100 }),
  });

  const { data: jobs } = useQuery({
    queryKey: ['jobs', 'list'],
    queryFn: () => jobService.list({ limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => applicationService.create(data),
    onSuccess: () => {
      toast.success('Application tracked');
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      setIsOpen(false);
      resetForm();
    },
    onError: () => toast.error('Failed to track application'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => applicationService.update(id, data),
    onSuccess: () => {
      toast.success('Application updated');
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      setIsOpen(false);
      setEditing(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => applicationService.delete(id),
    onSuccess: () => {
      toast.success('Application deleted');
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
    onError: () => toast.error('Failed to delete application'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      job_opportunity_id: parseInt(form.job_opportunity_id),
      cv_id: form.cv_id ? parseInt(form.cv_id) : null,
    };
    if (editing) {
      updateMutation.mutate({ id: editing.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const resetForm = () => {
    setForm({
      job_opportunity_id: '', cv_id: '', status: 'applied',
      application_date: '', deadline: '', notes: '',
    });
  };

  const openCreate = () => {
    setEditing(null);
    resetForm();
    setIsOpen(true);
  };

  const openEdit = (app: JobApplication) => {
    setEditing(app);
    setForm({
      job_opportunity_id: app.job_opportunity_id,
      cv_id: app.cv_id || '',
      status: app.status,
      application_date: app.application_date ? new Date(app.application_date).toISOString().split('T')[0] : '',
      deadline: app.deadline ? new Date(app.deadline).toISOString().split('T')[0] : '',
      notes: app.notes || '',
    });
    setIsOpen(true);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
          <p className="text-sm text-gray-500 mt-1">Track your job applications and their status</p>
        </div>
        <Button onClick={openCreate}><Plus className="w-4 h-4" /> Track Application</Button>
      </div>

      {applications && applications.length > 0 ? (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Job</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Applied</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notes</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900">Job #{app.job_opportunity_id}</div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge color={getStatusColor(app.status)}>{humanize(app.status)}</Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {formatDate(app.application_date)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">
                      {app.notes || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={() => openEdit(app)}><Edit2 className="w-3 h-3" /></Button>
                        <Button variant="outline" size="sm" onClick={() => deleteMutation.mutate(app.id)}><Trash2 className="w-3 h-3 text-red-500" /></Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        <Card>
          <EmptyState
            icon={<Send className="w-12 h-12" />}
            title="No applications yet"
            description="Track your first job application here."
            action={<Button onClick={openCreate}><Plus className="w-4 h-4" /> Track First</Button>}
          />
        </Card>
      )}

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title={editing ? 'Edit Application' : 'Track Application'} size="md">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Job</Label>
            <select
              value={form.job_opportunity_id}
              onChange={(e) => setForm({ ...form, job_opportunity_id: e.target.value })}
              className="w-full h-10 rounded-md border border-gray-300 px-3"
              required
            >
              <option value="">Select a job</option>
              {jobs?.map((job) => (
                <option key={job.id} value={job.id}>{job.title} @ {job.company}</option>
              ))}
            </select>
          </div>
          <div>
            <Label>Status</Label>
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
              className="w-full h-10 rounded-md border border-gray-300 px-3"
            >
              {STATUSES.map((s) => <option key={s} value={s}>{humanize(s)}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Application Date</Label>
              <Input type="date" value={form.application_date} onChange={(e) => setForm({ ...form, application_date: e.target.value })} />
            </div>
            <div>
              <Label>Deadline</Label>
              <Input type="date" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} />
            </div>
          </div>
          <div>
            <Label>Notes</Label>
            <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={3} />
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
