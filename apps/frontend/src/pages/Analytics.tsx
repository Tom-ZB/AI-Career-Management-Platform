import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { BarChart3, TrendingUp, Calendar, Users, FileText } from 'lucide-react';
import { analyticsService, applicationService, jobService, cvService, interviewService } from '../services';
import { Card, CardHeader, CardTitle, CardContent, LoadingSpinner } from '../components/ui';
import { humanize } from '../lib/utils';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1'];

export default function Analytics() {
  const [period, setPeriod] = useState('30d');

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['analytics', 'dashboard'],
    queryFn: analyticsService.dashboard,
  });

  const { data: appStats } = useQuery({
    queryKey: ['applications', 'stats'],
    queryFn: applicationService.stats,
  });

  const statusData = appStats?.by_status
    ? Object.entries(appStats.by_status).map(([name, value]) => ({ name: humanize(name), value }))
    : [];

  const sourceData = dashboard?.jobs?.by_source
    ? Object.entries(dashboard.jobs.by_source).map(([name, value]) => ({ name, value }))
    : [];

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-sm text-gray-500 mt-1">Insights into your job search performance</p>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={FileText} label="Total Applications" value={dashboard?.applications?.total || 0} color="bg-blue-500" />
        <StatCard icon={TrendingUp} label="Response Rate" value={`${dashboard?.response_rate || 0}%`} color="bg-green-500" />
        <StatCard icon={Calendar} label="Upcoming Interviews" value={dashboard?.interviews?.upcoming || 0} color="bg-purple-500" />
        <StatCard icon={Users} label="Pending Follow-ups" value={dashboard?.follow_ups?.pending || 0} color="bg-orange-500" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" /> Applications by Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statusData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" /> Jobs by Source
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sourceData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sourceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent activity summary */}
      <Card>
        <CardHeader>
          <CardTitle>Activity Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-500">Interviews Completed</p>
              <p className="text-2xl font-bold text-blue-600">{dashboard?.interviews?.completed || 0}</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-500">Total Job Matches</p>
              <p className="text-2xl font-bold text-green-600">{dashboard?.match_rate || 0}%</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-500">Active Opportunities</p>
              <p className="text-2xl font-bold text-purple-600">{dashboard?.jobs?.total || 0}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: number | string; color: string }) {
  return (
    <Card>
      <CardContent className="p-5 flex items-center gap-4">
        <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}
