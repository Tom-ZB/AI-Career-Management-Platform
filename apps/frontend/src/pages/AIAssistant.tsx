import { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { aiService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import type { ChatMessage } from '../types';

const SUGGESTIONS = [
  'Analyze my CV and suggest improvements',
  'Match my CV with my saved jobs',
  'Generate a cover letter for job #1',
  'Summarize my recent applications',
  'Prepare me for my next interview',
];

export default function AIAssistant() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatMutation = useMutation({
    mutationFn: (message: string) => aiService.chat(message, sessionId),
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), session_id: data.session_id, role: 'assistant', content: data.message, created_at: new Date().toISOString() } as ChatMessage,
      ]);
    },
    onError: () => {
      toast.error('AI service unavailable');
      setMessages((prev) => [...prev, { id: Date.now(), session_id: sessionId || '', role: 'assistant', content: 'Sorry, I could not process your request. Please make sure the AI service is configured.', created_at: new Date().toISOString() } as ChatMessage]);
    },
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;
    const userMsg: ChatMessage = {
      id: Date.now(),
      session_id: sessionId || '',
      role: 'user',
      content: input.trim(),
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input.trim();
    setInput('');
    chatMutation.mutate(currentInput);
  };

  return (
    <div className="h-[calc(100vh-7rem)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900">AI Career Assistant</h1>
        <p className="text-sm text-gray-500 mt-1">Ask anything about your career, CV, or job search</p>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardHeader className="border-b border-gray-200 bg-gray-50/50">
          <CardTitle className="flex items-center gap-2 text-base">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            AI Assistant
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">How can I help your career today?</h3>
              <p className="text-sm text-gray-500 max-w-md mb-6">I can analyze your CV, match you with jobs, generate cover letters, prepare you for interviews, and answer questions about your career data.</p>
              <div className="flex flex-wrap justify-center gap-2 max-w-lg">
                {SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => { setInput(suggestion); }}
                    className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-brand-50 hover:text-brand-700 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-brand-100 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-brand-600" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2.5 text-sm ${
                    msg.role === 'user'
                      ? 'bg-brand-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  {msg.content}
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-gray-600" />
                  </div>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </CardContent>

        <div className="p-4 border-t border-gray-200 bg-white">
          <form onSubmit={handleSend} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about your career..."
              className="flex-1"
              disabled={chatMutation.isPending}
            />
            <Button
              type="submit"
              disabled={chatMutation.isPending || !input.trim()}
              loading={chatMutation.isPending}
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
