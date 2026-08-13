import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, FileText, Trash2, Download, Upload } from 'lucide-react';
import toast from 'react-hot-toast';
import { documentService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Textarea, LoadingSpinner, EmptyState, Modal, Badge } from '../components/ui';
import { formatDate, formatFileSize, getStatusColor, humanize } from '../lib/utils';
import type { Document } from '../types';

const DOC_TYPES = ['cv', 'cover_letter', 'certificate', 'transcript', 'portfolio', 'job_description', 'other'];

export default function Documents() {
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('cv');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentService.list({ limit: 100 }),
  });

  const uploadMutation = useMutation({
    mutationFn: () => documentService.upload(selectedFile!, docType, title),
    onSuccess: () => {
      toast.success('Document uploaded');
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setIsOpen(false);
      setSelectedFile(null);
      setTitle('');
      setDescription('');
    },
    onError: () => toast.error('Failed to upload document'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentService.delete(id),
    onSuccess: () => {
      toast.success('Document deleted');
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      toast.error('Please select a file');
      return;
    }
    uploadMutation.mutate();
  };

  const getIcon = (type: string) => {
    const color = type === 'cv' ? 'text-blue-600' : type === 'cover_letter' ? 'text-purple-600' : 'text-gray-600';
    return <FileText className={`w-8 h-8 ${color}`} />;
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-sm text-gray-500 mt-1">Manage your CVs, cover letters, and supporting files</p>
        </div>
        <Button onClick={() => setIsOpen(true)}><Plus className="w-4 h-4" /> Upload</Button>
      </div>

      {documents && documents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map((doc) => (
            <Card key={doc.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                    {getIcon(doc.document_type)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-gray-900 truncate">{doc.title || doc.file_name}</h3>
                    <p className="text-xs text-gray-500 mt-1">{humanize(doc.document_type)} · {formatFileSize(doc.file_size)}</p>
                    <p className="text-xs text-gray-400 mt-1">{formatDate(doc.uploaded_at)}</p>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button variant="outline" size="sm"><Download className="w-3 h-3" /> Download</Button>
                  <Button variant="outline" size="sm" onClick={() => deleteMutation.mutate(doc.id)}><Trash2 className="w-3 h-3 text-red-500" /></Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<FileText className="w-12 h-12" />}
            title="No documents yet"
            description="Upload your CV, certificates, and other career files."
            action={<Button onClick={() => setIsOpen(true)}><Upload className="w-4 h-4" /> Upload First</Button>}
          />
        </Card>
      )}

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title="Upload Document" size="md">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Document Type</Label>
            <select value={docType} onChange={(e) => setDocType(e.target.value)} className="w-full h-10 rounded-md border border-gray-300 px-3">
              {DOC_TYPES.map((t) => <option key={t} value={t}>{humanize(t)}</option>)}
            </select>
          </div>
          <div>
            <Label>Title (optional)</Label>
            <Input value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div>
            <Label>File</Label>
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
              <Upload className="w-8 h-8 text-gray-400 mb-2" />
              <span className="text-sm text-gray-500">
                {selectedFile ? selectedFile.name : 'Click or drag file to upload'}
              </span>
              <input
                type="file"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && setSelectedFile(e.target.files[0])}
              />
            </label>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsOpen(false)} type="button">Cancel</Button>
            <Button type="submit" loading={uploadMutation.isPending}>Upload</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

const Label = ({ children, htmlFor }: { children: React.ReactNode; htmlFor?: string }) => (
  <label htmlFor={htmlFor} className="block text-sm font-medium text-gray-700 mb-1.5">{children}</label>
);
