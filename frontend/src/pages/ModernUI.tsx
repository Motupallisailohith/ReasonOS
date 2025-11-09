import React, { useState } from 'react';
import { Loader, Brain, Search } from 'lucide-react';

// --- Interfaces ---
interface Stats {
  files_parsed: number;
  functions_found: number;
  edges_created: number;
  time_taken_seconds: number;
}

interface AIResult {
  understood_intent: string;
  confidence: number;
  ai_reasoning: string;
  analysis_result?: {
    function_name: string;
    summary: { total_usages: number; total_files: number; risk_level: string; risk_score: number };
    modules: Array<{
      module_name: string;
      file_path: string;
      criticality: string;
      impact_description: string;
      usages: Array<{ line: number; context: string }>;
    }>;
    business_impact: { revenue_impact_range: string; affected_users: string; estimated_recovery_time: string };
    safety_recommendation: string;
  };
}

// --- Main Component ---
const ModernUI: React.FC = () => {
  const [repoPath, setRepoPath] = useState('C:\\Users\\sailo\\DistributedSystems-2PC');
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [stats, setStats] = useState<Stats | null>(null);
  const [query, setQuery] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);
  const [result, setResult] = useState<AIResult | null>(null);

  const analyzeRepo = async () => {
    setAnalyzing(true);
    setResult(null); // Clear previous AI results
    try {
      const res = await fetch('http://localhost:8000/api/v1/graph/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: repoPath }),
      });
      if (!res.ok) throw new Error('Analysis failed');
      const data = await res.json();
      setStats(data.statistics);
      setAnalyzed(true);
    } catch (err) {
      console.error('Failed to analyze repository', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim() || !analyzed) return;
    setQueryLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/graph/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: repoPath, prompt: query, use_ai: true }),
      });
      if (!res.ok) throw new Error('Query failed');
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error('Failed to process query', err);
    } finally {
      setQueryLoading(false);
    }
  };

  return (
    <main className="bg-black">
      {/* Hero Section */}
      <section className="relative w-full bg-black" style={{ height: 'calc(100vh - 60px)' }}>
        <div className="flex items-center justify-center flex-col h-5/6 w-full">
          <p className="text-center font-semibold text-5xl md:text-6xl text-gray-100 max-md:mb-10">
            ReasonOS
          </p>
          <p className="text-center text-xl text-[#86868b] mt-6 max-w-2xl px-6">
            An AI-powered operating system for semantic code understanding and generation.
          </p>
        </div>
      </section>

      {/* Two-Tile Layout */}
      <div className="screen-max-width">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 common-padding">
          
          {/* Tile 1: Semantic Understanding */}
          <div className="p-8 bg-[#101010] rounded-3xl border border-[#424245]">
            <div className="flex items-center gap-4 mb-8">
              <div className="p-3 bg-[#2997FF]/20 rounded-full">
                <Search className="w-6 h-6 text-[#2997FF]" />
              </div>
              <h2 className="text-3xl font-semibold text-white">Semantic Understanding</h2>
            </div>
            <p className="text-[#86868b] mb-8">Analyze a repository to build a semantic graph of its codebase, understanding functions, dependencies, and structure.</p>
            
            <div className="space-y-4">
              <input
                type="text"
                value={repoPath}
                onChange={(e) => setRepoPath(e.target.value)}
                placeholder="Enter repository path"
                className="w-full px-5 py-4 bg-[#1d1d1f] border border-[#424245] rounded-xl text-white placeholder-[#86868b] focus:outline-none focus:border-[#2997FF] text-lg"
              />
              <button
                onClick={analyzeRepo}
                disabled={analyzing}
                className="w-full px-5 py-4 rounded-xl bg-[#2997FF] hover:bg-[#147CE5] text-white font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {analyzing ? <Loader className="animate-spin" /> : 'Analyze Repository'}
              </button>
            </div>

            {stats && (
              <div className="mt-8 pt-8 border-t border-[#424245] grid grid-cols-2 gap-6">
                <StatItem value={stats.files_parsed} label="Files Parsed" />
                <StatItem value={stats.functions_found} label="Functions Found" />
                <StatItem value={stats.edges_created} label="Dependencies" />
                <StatItem value={`${stats.time_taken_seconds.toFixed(1)}s`} label="Time Taken" />
              </div>
            )}
          </div>

          {/* Tile 2: AI Generation */}
          <div className={`p-8 bg-[#101010] rounded-3xl border border-[#424245] transition-opacity duration-500 ${analyzed ? 'opacity-100' : 'opacity-50'}`}>
            <div className="flex items-center gap-4 mb-8">
              <div className="p-3 bg-[#30d158]/20 rounded-full">
                <Brain className="w-6 h-6 text-[#30d158]" />
              </div>
              <h2 className="text-3xl font-semibold text-white">AI Generation</h2>
            </div>
            <p className="text-[#86868b] mb-8">Ask questions about the analyzed codebase. The AI will reason about the code to provide insights and risk assessments.</p>
            
            <div className="space-y-4">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                placeholder="e.g., Is it safe to delete runTransaction?"
                className="w-full px-5 py-4 bg-[#1d1d1f] border border-[#424245] rounded-xl text-white placeholder-[#86868b] focus:outline-none focus:border-[#30d158] text-lg"
                disabled={!analyzed}
              />
              <button
                onClick={handleQuery}
                disabled={queryLoading || !query.trim() || !analyzed}
                className="w-full px-5 py-4 rounded-xl bg-[#30d158] hover:bg-[#28a745] text-black font-bold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {queryLoading ? <Loader className="animate-spin" /> : 'Ask AI'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* AI Results Section */}
      {result && (
        <section className="common-padding bg-[#101010] w-screen overflow-hidden">
          <div className="screen-max-width">
            <div className="mb-12">
              <h1 className="section-heading">AI Analysis.</h1>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-8">
                {/* Risk Assessment */}
                <div className="p-8 bg-[#1d1d1f] rounded-3xl border border-[#424245]">
                  <h3 className="text-2xl font-semibold mb-2">Risk Assessment</h3>
                  <code className="text-[#afafaf] font-mono">{result.analysis_result?.function_name}</code>
                  <div className="flex items-end justify-between mt-6">
                    <div>
                      <p className="text-sm text-[#86868b]">Risk Score</p>
                      <p className="text-7xl font-semibold">{result.analysis_result?.summary.risk_score}%</p>
                    </div>
                    <p className={`text-2xl font-semibold uppercase ${result.analysis_result?.summary.risk_level === 'low' ? 'text-[#30d158]' : 'text-[#ff9f0a]'}`}>
                      {result.analysis_result?.summary.risk_level}
                    </p>
                  </div>
                </div>
                
                {/* Business Impact */}
                <div className="p-8 bg-[#1d1d1f] rounded-3xl border border-[#424245]">
                  <h3 className="text-2xl font-semibold mb-6">Business Impact</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <StatItem value={result.analysis_result?.business_impact.revenue_impact_range} label="Revenue" />
                    <StatItem value={result.analysis_result?.business_impact.affected_users} label="Users" />
                    <StatItem value={result.analysis_result?.business_impact.estimated_recovery_time} label="Recovery" />
                  </div>
                </div>
              </div>

              {/* AI Understanding */}
              <div className="p-8 bg-[#1d1d1f] rounded-3xl border border-[#424245] space-y-6">
                <h3 className="text-2xl font-semibold">AI Understanding</h3>
                <p className="text-[#afafaf] text-lg">{result.understood_intent}</p>
                <div>
                  <div className="flex justify-between items-baseline mb-2">
                    <p className="text-sm text-[#86868b]">Confidence</p>
                    <p className="text-3xl font-semibold">{(result.confidence * 100).toFixed(0)}%</p>
                  </div>
                  <div className="h-2 bg-[#424245] rounded-full"><div className="h-full bg-[#2997FF] rounded-full" style={{width: `${result.confidence * 100}%`}}></div></div>
                </div>
                <p className="text-[#86868b] italic border-l-2 border-[#424245] pl-4">"{result.ai_reasoning}"</p>
              </div>
            </div>

            {/* Affected Modules */}
            {result.analysis_result && result.analysis_result.modules.length > 0 && (
              <div className="mt-16">
                <h2 className="section-heading mb-8">Affected Modules.</h2>
                <div className="space-y-4">
                  {result.analysis_result.modules.map((mod, i) => (
                    <div key={i} className="p-6 bg-[#1d1d1f] rounded-2xl border border-[#424245]">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="text-xl font-semibold text-white">{mod.module_name}</h4>
                          <p className="text-xs text-[#86868b] font-mono">{mod.file_path}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${mod.criticality === 'low' ? 'bg-[#30d158]/20 text-[#30d158]' : 'bg-[#ff9f0a]/20 text-[#ff9f0a]'}`}>
                          {mod.criticality}
                        </span>
                      </div>
                      <p className="text-[#afafaf] mb-4">{mod.impact_description}</p>
                      {mod.usages[0] && (
                        <div className="p-4 bg-black/50 rounded-xl border border-[#424245]">
                          <code className="text-sm text-[#30d158] font-mono">{mod.usages[0].context}</code>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="py-12 border-t border-[#424245]">
        <div className="screen-max-width text-center">
          <p className="text-sm text-[#86868b]">
            Powered by Gemini AI, Tree-sitter, and NetworkX
          </p>
        </div>
      </footer>
    </main>
  );
};

// --- Helper Components ---
const StatItem: React.FC<{ value: string | number | undefined; label: string }> = ({ value, label }) => (
  <div>
    <p className="text-3xl font-semibold text-white">{value}</p>
    <p className="text-sm text-[#86868b]">{label}</p>
  </div>
);

export default ModernUI;
