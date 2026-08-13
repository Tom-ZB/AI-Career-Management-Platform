import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Bell, Check, Trash2, Edit2, Calendar } from 'lucide-react';
import toast from 'react-hot-toast';
import { followUpService, applicationService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Textarea, LoadingSpinner, EmptyState, Modal, Badge } from '../components/ui';
import { formatDate, getStatusColor, daysUntil, humanize } from '../lib/utils';
import type { FollowUp } from '../types';

const TYPES = ['email', 'phone_call', 'message', 'meeting', 'thank_you', 'follow_up_email', 'networking'];
const STATUSES = ['pending', 'completed', 'missed', 'cancelled'];

export default function FollowUps() {
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<FollowUp | null>(null);
  const [form, setForm] = useState<any>({
    application_id: '', follow_up_type: 'email', title: '', description: '',
    scheduled_at: '', priority: 2, status: 'pending', notes: '',
  });

  const { data: followUps, isLoading } = useQuery({
    queryKey: ['follow-ups'],
    queryFn: () => followUpService.list({ limit: 100 }),
  });

  const { data: applications } = useQuery({
    queryKey: ['applications', 'list'],
    queryFn: () => applicationService.list({ limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => followUpService.create(data),
    onSuccess: () => {
      toast.success('Follow-up created');
      queryClient.invalidateQueries({ queryKey: ['follow-ups'] });
      setIsOpen(false);
      resetForm();
    },
    onError: () => toast.error('Failed to create follow-up'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => followUpService.update(id, data),
    onSuccess: () => {
      toast.success('Follow-up updated');
      queryClient.invalidateQueries({ queryKey: ['follow-ups'] });
      setIsOpen(false);
      setEditing(null);
    },
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => followUpService.complete(id),
    onSuccess: () => {
      toast.success('Follow-up completed');
      queryClient.invalidateQueries({ queryKey: ['follow-ups'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => followUpService.delete(id),
    onSuccess: () => {
      toast.success('Follow-up deleted');
      queryClient.invalidateQueries({ queryKey: ['follow-ups'] });
    },
  });

  const resetForm = () => {
    setForm({
      application_id: '', follow_up_type: 'email', title: '', description: '',
      scheduled_at: '', priority: 2, status: 'pending', notes: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      application_id: form.application_id ? parseInt(form.application_id) : null,
      priority: parseInt(form.priority) || 2,
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

  const openEdit = (fu: FollowUp) => {
    setEditing(fu);
    setForm({
      application_id: String(fu.application_id || ''),
      follow_up_type: fu.follow_up_type,
      title: fu.title || '',
      description: fu.description || '',
      scheduled_at: fu.scheduled_at ? new Date(fu.scheduled_at).toISOString().slice(0, 16) : '',
      priority: fu.priority,
      status: fu.status,
      notes: fu.notes || '',
    });
    setIsOpen(true);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Follow-ups</h1>
          <p className="text-sm text-gray-500 mt-1">Stay on top of your networking and outreach</p>
        </div>
        <Button onClick={openCreate}><Plus className="w-4 h-4" /> Add Follow-up</Button>
      </div>

      {followUps && followUps.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {followUps.map((fu) => {
            const days = daysUntil(fu.scheduled_at);
            return (
              <Card key={fu.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        fu.status === 'completed' ? 'bg-green-100' : days < 0 ? 'bg-red-100' : 'bg-yellow-100'
                      }`}>
                        <Bell className={`w-5 h-5 ${
                          fu.status === 'completed' ? 'text-green-600' : days < 0 ? 'text-red-600' : 'text-yellow-600'
                        }`} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{fu.title || humanize(fu.follow_up_type)}</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          {formatDate(fu.scheduled_at)} · {fu.priority === 3 ? 'High' : fu.priority === 2 ? 'Medium' : 'Low'} priority
                        </p>
                        {fu.notes && <p className="text-sm text-gray-600 mt-2">{fu.notes}</p>}
                      </div>
                    </div>
                    <Badge color={getStatusColor(fu.status)}>{humanize(fu.status)}</Badge>
                  </div>
                  <div className="flex gap-2 mt-4">
                    {fu.status !== 'completed' && (
                      <Button variant="outline" size="sm" onClick={() => completeMutation.mutate(fu.id)}>
                        <Check className="w-3 h-3" /> Complete
                      </Button>
                    )}
                    <Button variant="outline" size="sm" onClick={() => openEdit(fu)}><Edit2 className="w-3 h-3" /></Button>
                    <Button variant="outline" size="sm" onClick={() => deleteMutation.mutate(fu.id)}><Trash2 className="w-3 h-3 text-red-500" /></Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<Bell className="w-12 h-12" />}
            title="No follow-ups yet"
            description="Keep track of outreach, thank you notes, and reminders."
            action={<Button onClick={openCreate}><Plus className="w-4 h-4" /> Add First</Button>}
          />
        </Card>
      )}

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title={editing ? 'Edit Follow-up' : 'Add Follow-up'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Application</Label>
            <select
              value={form.application_id}
              onChange={(e) => setForm({ ...form, application_id: e.target.value })}
              className="w-full h-10 rounded-md border border-gray-300 px-3"
            >
              <option value="">Optional: Select application</option>
              {applications?.map((app) => (
                <option key={app.id} value={app.id}>Application #{app.id}</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Type</Label>
              <select value={form.follow_up_type} onChange={(e) => setForm({ ...form, follow_up_type: e.target.value })} className="w-full h-10 rounded-md border border-gray-300 px-3">
                {TYPES.map((t) => <option key={t} value={t}>{humanize(t)}</option>)}
              </select>
            </div>
            <div>
              <Label>Priority</Label>
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })} className="w-full h-10 rounded-md border border-gray-300 px-3">
                <option value={1}>Low</option>
                <option value={2}>Medium</option>
                <option value={3}>High</option>
              </select>
            </div>
          </div>
          <div>
            <Label>Title</Label>
            <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div>
            <Label>Scheduled At</Label>
            <Input type="datetime-local" value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })} required />
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
