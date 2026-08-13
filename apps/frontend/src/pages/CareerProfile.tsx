import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { User, Briefcase, GraduationCap, Mail, Phone, MapPin, Linkedin, Github, Plus, Save } from 'lucide-react';
import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { profileService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Textarea, Label, LoadingSpinner } from '../components/ui';

export default function CareerProfile() {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<any>({
    full_name: '', title: '', summary: '',
    skills: [], experience_years: 0,
    contact_info: {}, social_links: {},
  });
  const [skillInput, setSkillInput] = useState('');

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: profileService.get,
  });

  useEffect(() => {
    if (profile) {
      setForm({
        full_name: profile.full_name || '',
        title: profile.title || '',
        summary: profile.summary || '',
        skills: profile.skills || [],
        experience_years: profile.experience_years || 0,
        contact_info: profile.contact_info || {},
        social_links: profile.social_links || {},
      });
    }
  }, [profile]);

  const saveMutation = useMutation({
    mutationFn: (data: any) =>
      profile?.id ? profileService.update(data) : profileService.create({ ...data, user_id: 1 }),
    onSuccess: () => {
      toast.success('Profile saved!');
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      setEditing(false);
    },
    onError: () => toast.error('Failed to save profile'),
  });

  const handleAddSkill = () => {
    if (skillInput.trim() && !form.skills.includes(skillInput.trim())) {
      setForm({ ...form, skills: [...form.skills, skillInput.trim()] });
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skill: string) => {
    setForm({ ...form, skills: form.skills.filter((s: string) => s !== skill) });
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Career Profile</h1>
          <p className="text-sm text-gray-500 mt-1">Your master career information</p>
        </div>
        <Button
          variant={editing ? 'default' : 'outline'}
          onClick={() => editing ? saveMutation.mutate(form) : setEditing(true)}
          loading={saveMutation.isPending}
        >
          {editing ? (<><Save className="w-4 h-4" /> Save</>) : 'Edit Profile'}
        </Button>
      </div>

      {/* Personal Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" /> Personal Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Full Name</Label>
              <Input
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                disabled={!editing}
              />
            </div>
            <div>
              <Label>Professional Title</Label>
              <Input
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                disabled={!editing}
                placeholder="Senior Full-Stack Engineer"
              />
            </div>
          </div>
          <div>
            <Label>Summary</Label>
            <Textarea
              value={form.summary}
              onChange={(e) => setForm({ ...form, summary: e.target.value })}
              disabled={!editing}
              rows={4}
              placeholder="Brief professional summary..."
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Years of Experience</Label>
              <Input
                type="number"
                value={form.experience_years}
                onChange={(e) => setForm({ ...form, experience_years: parseInt(e.target.value) || 0 })}
                disabled={!editing}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Skills */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Briefcase className="w-5 h-5" /> Skills
          </CardTitle>
        </CardHeader>
        <CardContent>
          {editing && (
            <div className="flex gap-2 mb-4">
              <Input
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
                placeholder="Add a skill..."
                className="flex-1"
              />
              <Button onClick={handleAddSkill} variant="outline">
                <Plus className="w-4 h-4" />
              </Button>
            </div>
          )}
          <div className="flex flex-wrap gap-2">
            {form.skills.map((skill: string) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-brand-50 text-brand-700 text-sm"
              >
                {skill}
                {editing && (
                  <button onClick={() => handleRemoveSkill(skill)} className="text-brand-400 hover:text-brand-600">
                    ×
                  </button>
                )}
              </span>
            ))}
            {form.skills.length === 0 && (
              <p className="text-sm text-gray-400">No skills added yet</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Contact Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Phone className="w-5 h-5" /> Contact Information
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label>Phone</Label>
            <Input
              value={form.contact_info?.phone || ''}
              onChange={(e) => setForm({
                ...form,
                contact_info: { ...form.contact_info, phone: e.target.value }
              })}
              disabled={!editing}
            />
          </div>
          <div>
            <Label>City</Label>
            <Input
              value={form.contact_info?.city || ''}
              onChange={(e) => setForm({
                ...form,
                contact_info: { ...form.contact_info, city: e.target.value }
              })}
              disabled={!editing}
            />
          </div>
          <div>
            <Label>Country</Label>
            <Input
              value={form.contact_info?.country || ''}
              onChange={(e) => setForm({
                ...form,
                contact_info: { ...form.contact_info, country: e.target.value }
              })}
              disabled={!editing}
            />
          </div>
        </CardContent>
      </Card>

      {/* Social Links */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Linkedin className="w-5 h-5" /> Social Links
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label>LinkedIn</Label>
            <Input
              value={form.social_links?.linkedin || ''}
              onChange={(e) => setForm({
                ...form,
                social_links: { ...form.social_links, linkedin: e.target.value }
              })}
              disabled={!editing}
              placeholder="https://linkedin.com/in/..."
            />
          </div>
          <div>
            <Label>GitHub</Label>
            <Input
              value={form.social_links?.github || ''}
              onChange={(e) => setForm({
                ...form,
                social_links: { ...form.social_links, github: e.target.value }
              })}
              disabled={!editing}
              placeholder="https://github.com/..."
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
