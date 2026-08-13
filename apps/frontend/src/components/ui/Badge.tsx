import { HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  color?: string;
}

const Badge = ({ className, color, children, ...props }: BadgeProps) => (
  <span
    className={cn(
      'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
      color || 'bg-gray-100 text-gray-800',
      className
    )}
    {...props}
  >
    {children}
  </span>
);

export { Badge };
