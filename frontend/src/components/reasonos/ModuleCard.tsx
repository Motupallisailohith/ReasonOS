import { AlertCircle, AlertTriangle, CheckCircle2 } from 'lucide-react';
import type { AffectedModule } from '../../types/schema';
import { RiskBadge } from './RiskBadge';

interface ModuleCardProps {
  module: AffectedModule;
}

export function ModuleCard({ module }: ModuleCardProps) {
  const getCriticalityIcon = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'high':
        return <AlertCircle className="w-4 h-4 text-orange-500" />;
      case 'medium':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'low':
        return <CheckCircle2 className="w-4 h-4 text-blue-500" />;
      default:
        return <CheckCircle2 className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="group bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-6 hover:bg-white/10 transition-all">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {getCriticalityIcon(module.criticality)}
            <h4 className="text-lg font-semibold text-white">{module.module_name}</h4>
          </div>
          <p className="text-sm text-[#86868b] font-mono">{module.file_path}</p>
        </div>
        <RiskBadge level={module.criticality} size="sm" />
      </div>

      <p className="text-sm text-[#86868b] mb-4 leading-relaxed">{module.impact_description}</p>

      {module.usages[0] && (
        <div className="p-4 bg-black/40 rounded-xl border border-white/10">
          <div className="flex items-start justify-between mb-2">
            <code className="text-xs text-[#86868b]">Line {module.usages[0].line}</code>
          </div>
          <code className="text-sm text-green-400 font-mono break-all">
            {module.usages[0].context}
          </code>
        </div>
      )}

      {module.usages.length > 1 && (
        <p className="text-xs text-[#86868b] mt-2">
          +{module.usages.length - 1} more usage{module.usages.length - 1 !== 1 ? 's' : ''}
        </p>
      )}
    </div>
  );
}