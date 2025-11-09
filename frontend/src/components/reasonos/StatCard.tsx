import type { LucideIcon } from 'lucide-react';
import { Tooltip } from 'react-tooltip';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  tooltip?: string;
}

export function StatCard({ icon: Icon, label, value, tooltip }: StatCardProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-[#86868b]">
        <Icon className="w-4 h-4" />
        <p className="text-sm" data-tooltip-id={label} data-tooltip-content={tooltip}>{label}</p>
        {tooltip && <Tooltip id={label} />}
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  );
}
