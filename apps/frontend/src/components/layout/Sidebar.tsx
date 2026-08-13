import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, User, FileText, Briefcase, Send,
  Calendar, Bell, FolderOpen, Bot, BarChart3, X,
} from 'lucide-react';
import { cn } from '../../lib/utils';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/profile', label: 'Career Profile', icon: User },
  { to: '/cvs', label: 'My CVs', icon: FileText },
  { to: '/jobs', label: 'Job Opportunities', icon: Briefcase },
  { to: '/applications', label: 'Applications', icon: Send },
  { to: '/interviews', label: 'Interviews', icon: Calendar },
  { to: '/follow-ups', label: 'Follow-ups', icon: Bell },
  { to: '/documents', label: 'Documents', icon: FolderOpen },
  { to: '/ai-assistant', label: 'AI Assistant', icon: Bot },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
];

export default function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          'fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 flex flex-col transition-transform duration-300',
          open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-gray-900">AI Career</span>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden text-gray-500 hover:text-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  )
                }
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <p className="text-xs text-gray-400 text-center">v1.0.0 © 2026</p>
        </div>
      </aside>
    </>
  );
}
