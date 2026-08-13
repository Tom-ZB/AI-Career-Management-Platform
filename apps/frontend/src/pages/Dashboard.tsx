import { useQuery } from '@tanstack/react-query';
import {
  Send, Briefcase, Calendar, Bell, TrendingUp,
  CheckCircle2, Clock, Target,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { analyticsService, interviewService, followUpService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Badge, LoadingSpinner } from '../components/ui';
import { formatDate, getStatusColor, daysUntil } from '../lib/utils';

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: analyticsService.dashboard,
  });

  const { data: interviews } = useQuery({
    queryKey: ['interviews', 'upcoming'],
    queryFn: () => interviewService.list({ upcoming_only: true, limit: 5 }),
  });

  const { data: followUps } = useQuery({
    queryKey: ['follow-ups', 'pending'],
    queryFn: () => followUpService.list({ status: 'pending', limit: 5 }),
  });

  if (isLoading) return <LoadingSpinner />;

  const statCards = [
    {
      label: 'Applications',
      value: stats?.applications?.total || 0,
      icon: Send,
      color: 'bg-blue-500',
      link: '/applications',
    },
    {
      label: 'Job Opportunities',
      value: stats?.jobs?.total || 0,
      icon: Briefcase,
      color: 'bg-purple-500',
      link: '/jobs',
    },
    {
      label: 'Upcoming Interviews',
      value: stats?.interviews?.upcoming || 0,
      icon: Calendar,
      color: 'bg-green-500',
      link: '/interviews',
    },
    {
      label: 'Pending Follow-ups',
      value: stats?.follow_ups?.pending || 0,
      icon: Bell,
      color: 'bg-orange-500',
      link: '/follow-ups',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <Link key={card.label} to={card.link}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">{card.label}</p>
                      <p className="text-2xl font-bold text-gray-900 mt-1">{card.value}</p>
                    </div>
                    <div className={`w-12 h-12 rounded-lg ${card.color} flex items-center justify-center`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming interviews */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Upcoming Interviews</CardTitle>
            <Link to="/interviews" className="text-sm text-brand-600 hover:text-brand-700">
              View all
            </Link>
          </CardHeader>
          <CardContent>
            {interviews && interviews.length > 0 ? (
              <div className="space-y-3">
                {interviews.map((interview) => (
                  <div key={interview.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                        <Calendar className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {interview.title || interview.interview_type}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatDateTime(interview.scheduled_at)}
                        </p>
                      </div>
                    </div>
                    <Badge color={getStatusColor(interview.status)}>
                      {interview.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p className="text-sm">No upcoming interviews</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pending follow-ups */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Pending Follow-ups</CardTitle>
            <Link to="/follow-ups" className="text-sm text-brand-600 hover:text-brand-700">
              View all
            </Link>
          </CardHeader>
          <CardContent>
            {followUps && followUps.length > 0 ? (
              <div className="space-y-3">
                {followUps.map((fu) => {
                  const days = daysUntil(fu.scheduled_at);
                  return (
                    <div key={fu.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          days < 0 ? 'bg-red-100' : 'bg-orange-100'
                        }`}>
                          <Bell className={`w-5 h-5 ${days < 0 ? 'text-red-600' : 'text-orange-600'}`} />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {fu.title || fu.follow_up_type}
                          </p>
                          <p className="text-xs text-gray-500">
                            Due: {formatDate(fu.scheduled_at)}
                          </p>
                        </div>
                      </div>
                      <Badge color={days < 0 ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}>
                        {days < 0 ? `${Math.abs(days)}d overdue` : `${days}d left`}
                      </Badge>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Bell className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p className="text-sm">No pending follow-ups</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Match Rate</p>
              <p className="text-xl font-bold text-gray-900">{stats?.match_rate || 0}%</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
              <Target className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Response Rate</p>
              <p className="text-xl font-bold text-gray-900">{stats?.response_rate || 0}%</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Completed Interviews</p>
              <p className="text-xl font-bold text-gray-900">{stats?.interviews?.completed || 0}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function formatDateTime(date: string): string {
  return new Date(date).toLocaleString('en-US', {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}
