import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Calendar, Clock, Video, MapPin, Trash2, Edit2, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { interviewService, applicationService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Textarea, LoadingSpinner, EmptyState, Modal, Badge } from '../components/ui';
import { formatDateTime, getStatusColor, humanize } from '../lib/utils';
import type { Interview } from '../types';

const TYPES = ['phone', 'video', 'onsite', 'technical', 'behavioral', 'case_study', 'final_round'];
const STATUSES = ['scheduled', 'completed', 'cancelled', 'rescheduled', 'no_show'];

export default function Interviews() {
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<Interview | null>(null);
  const [form, setForm] = useState<any>({
    application_id: '', interview_type: 'technical', title: '',
    scheduled_at: '', duration_minutes: 60, interviewer_name: '',
    meeting_url: '', location: '', status: 'scheduled', notes: '',
  });

  const { data: interviews, isLoading } = useQuery({
    queryKey: ['interviews'],
    queryFn: () => interviewService.list({ limit: 100 }),
  });

  const { data: applications } = useQuery({
    queryKey: ['applications', 'list'],
    queryFn: () => applicationService.list({ limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => interviewService.create(data),
    onSuccess: () => {
      toast.success('Interview scheduled');
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
      setIsOpen(false);
      resetForm();
    },
    onError: () => toast.error('Failed to schedule interview'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => interviewService.update(id, data),
    onSuccess: () => {
      toast.success('Interview updated');
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
      setIsOpen(false);
      setEditing(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => interviewService.delete(id),
    onSuccess: () => {
      toast.success('Interview deleted');
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
    },
  });

  const prepMutation = useMutation({
    mutationFn: (id: number) => interviewService.generatePrep(id),
    onSuccess: () => toast.success('Prep materials generated'),
    onError: () => toast.error('Failed to generate prep'),
  });

  const resetForm = () => {
    setForm({
      application_id: '', interview_type: 'technical', title: '',
      scheduled_at: '', duration_minutes: 60, interviewer_name: '',
      meeting_url: '', location: '', status: 'scheduled', notes: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      application_id: parseInt(form.application_id),
      duration_minutes: parseInt(form.duration_minutes) || 60,
    };
    if (editing) {
      updateMutation.mutate({ id: editing.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const openCreate = () => {
    setEditing(null);
    resetForm();
    setIsOpen(true);
  };

  const openEdit = (interview: Interview) => {
    setEditing(interview);
    setForm({
      application_id: String(interview.application_id),
      interview_type: interview.interview_type,
      title: interview.title || '',
      scheduled_at: interview.scheduled_at ? new Date(interview.scheduled_at).toISOString().slice(0, 16) : '',
      duration_minutes: interview.duration_minutes || 60,
      interviewer_name: interview.interviewer_name || '',
      meeting_url: interview.meeting_url || '',
      location: interview.location || '',
      status: interview.status,
      notes: interview.notes || '',
    });
    setIsOpen(true);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Interviews</h1>
          <p className="text-sm text-gray-500 mt-1">Schedule and prepare for your interviews</p>
        </div>
        <Button onClick={openCreate}><Plus className="w-4 h-4" /> Schedule Interview</Button>
      </div>

      {interviews && interviews.length > 0 ? (
        <div className="space-y-4">
          {interviews.map((interview) => (
            <Card key={interview.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-900">{interview.title || humanize(interview.interview_type)}</h3>
                        <Badge color={getStatusColor(interview.status)}>{humanize(interview.status)}</Badge>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {formatDateTime(interview.scheduled_at)} · {interview.duration_minutes || 60} min
                      </p>
                      {interview.interviewer_name && <p className="text-sm text-gray-600 mt-1">with {interview.interviewer_name}</p>}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => prepMutation.mutate(interview.id)}>
                      <Sparkles className="w-3 h-3" /> Prep
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => openEdit(interview)}><Edit2 className="w-3 h-3" /></Button>
                    <Button variant="outline" size="sm" onClick={() => deleteMutation.mutate(interview.id)}><Trash2 className="w-3 h-3 text-red-500" /></Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<Calendar className="w-12 h-12" />}
            title="No interviews scheduled"
            description="Schedule your first interview to get AI-powered prep."
            action={<Button onClick={openCreate}><Plus className="w-4 h-4" /> Schedule First</Button>}
          />
        </Card>
      )}

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title={editing ? 'Edit Interview' : 'Schedule Interview'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Application</Label>
            <select
              value={form.application_id}
              onChange={(e) => setForm({ ...form, application_id: e.target.value })}
              className="w-full h-10 rounded-md border border-gray-300 px-3"
              required
            >
              <option value="">Select application</option>
              {applications?.map((app) => (
                <option key={app.id} value={app.id}>Application #{app.id}</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Type</Label>
              <select value={form.interview_type} onChange={(e) => setForm({ ...form, interview_type: e.target.value })} className="w-full h-10 rounded-md border border-gray-300 px-3">
                {TYPES.map((t) => <option key={t} value={t}>{humanize(t)}</option>)}
              </select>
            </div>
            <div>
              <Label>Status</Label>
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} className="w-full h-10 rounded-md border border-gray-300 px-3">
                {STATUSES.map((s) => <option key={s} value={s}>{humanize(s)}</option>)}
              </select>
            </div>
          </div>
          <div>
            <Label>Title</Label>
            <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Scheduled At</Label>
              <Input type="datetime-local" value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })} required />
            </div>
            <div>
              <Label>Duration (min)</Label>
              <Input type="number" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })} />
            </div>
          </div>
          <div>
            <Label>Interviewer Name</Label>
            <Input value={form.interviewer_name} onChange={(e) => setForm({ ...form, interviewer_name: e.target.value })} />
          </div>
          <div>
            <Label>Notes</Label>
            <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={3} />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsOpen(false)} type="button">Cancel</Button>
            <Button type="submit" loading={createMutation.isPending || updateMutation.isPending}>{editing ? 'Update' : 'Schedule'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

const Label = ({ children, htmlFor }: { children: React.ReactNode; htmlFor?: string }) => (
  <label htmlFor={htmlFor} className="block text-sm font-medium text-gray-700 mb-1.5">{children}</label>
);
