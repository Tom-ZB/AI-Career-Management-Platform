import { ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface TableProps {
  headers: string[];
  children: ReactNode;
  className?: string;
}

export function Table({ headers, children, className }: TableProps) {
  return (
    <div className={cn('overflow-x-auto', className)}>
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            {headers.map((header, i) => (
              <th
                key={i}
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">{children}</tbody>
      </table>
    </div>
  );
}

export function TableRow({ children, className }: { children: ReactNode; className?: string }) {
  return <tr className={cn('hover:bg-gray-50 transition-colors', className)}>{children}</tr>;
}

export function TableCell({ children, className }: { children: ReactNode; className?: string }) {
  return <td className={cn('px-4 py-3 text-sm text-gray-900', className)}>{children}</td>;
}
