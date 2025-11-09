import { AlertCircle, AlertTriangle, Brain, CheckCircle2, ChevronRight, Clock, Code2, DollarSign, FileCode, GitBranch, Loader, Search, Sparkles, TrendingUp, Users, XCircle } from 'lucide-react';
import React, { useEffect, useState } from 'react';

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
  extracted_function: string;
  extracted_action: string;
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

const ModernUI: React.FC = () => {
  const [repoPath, setRepoPath] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [stats, setStats] = useState<Stats | null>(null);
  const [query, setQuery] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);
  const [result, setResult] = useState<AIResult | null>(null);
  const [error, setError] = useState<string>('');
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const analyzeRepo = async () => {
    setAnalyzing(true);
    setResult(null);
    setError('');
    try {
      const res = await fetch('http://localhost:8000/api/v1/graph/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: repoPath }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }
      const data = await res.json();
      setStats(data.statistics);
      setAnalyzed(true);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze repository');
      console.error('Analysis error:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim() || !analyzed) return;
    setQueryLoading(true);
    setError('');
    try {
      const res = await fetch('http://localhost:8000/api/v1/graph/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: repoPath, prompt: query, use_ai: true }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Query failed');
      }
      const data = await res.json();
      setResult(data);
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    } catch (err: any) {
      setError(err.message || 'Failed to process query');
      console.error('Query error:', err);
    } finally {
      setQueryLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'text-green-500';
      case 'medium': return 'text-yellow-500';
      case 'high': return 'text-orange-500';
      case 'critical': return 'text-red-500';
      default: return 'text-gray-400';
    }
  };

  const getRiskBg = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'bg-green-500/10 border-green-500/30';
      case 'medium': return 'bg-yellow-500/10 border-yellow-500/30';
      case 'high': return 'bg-orange-500/10 border-orange-500/30';
      case 'critical': return 'bg-red-500/10 border-red-500/30';
      default: return 'bg-gray-500/10 border-gray-500/30';
    }
  };

  const getCriticalityIcon = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical_path': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'secondary': return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'tertiary': return <CheckCircle2 className="w-4 h-4 text-blue-500" />;
      default: return <CheckCircle2 className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <main className="bg-black min-h-screen">
      {/* Navigation */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
        style={{
          backdropFilter: scrollY > 50 ? 'blur(20px)' : 'none',
          backgroundColor: scrollY > 50 ? 'rgba(0, 0, 0, 0.8)' : 'transparent',
          borderBottom: scrollY > 50 ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
        }}
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-white" />
            <span className="text-xl font-semibold text-white">ReasonOS</span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <a href="#analyze" className="text-[#86868b] hover:text-white transition-colors">Analyze</a>
            <a href="#query" className="text-[#86868b] hover:text-white transition-colors">Query</a>
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-[#86868b] hover:text-white transition-colors">Docs</a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative w-full min-h-screen flex items-center justify-center pt-20 pb-32 overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/20 via-black to-black"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/30 rounded-full blur-[120px] animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[120px] animate-pulse delay-1000"></div>

        <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-xl mb-8 animate-fade-in">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-[#86868b]">Powered by AI Semantic Analysis</span>
          </div>

          <h1 className="text-6xl md:text-8xl font-bold text-white mb-6 animate-fade-in-up leading-tight">
            Understand your
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              codebase deeply
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-[#86868b] max-w-3xl mx-auto mb-12 animate-fade-in-up delay-100 leading-relaxed">
            ReasonOS uses semantic graphs and AI to analyze code dependencies, assess risks, and provide intelligent insights for safer refactoring.
          </p>

          <button
            onClick={() => document.getElementById('analyze')?.scrollIntoView({ behavior: 'smooth' })}
            className="group inline-flex items-center gap-2 px-8 py-4 bg-white text-black rounded-full font-semibold hover:bg-gray-100 transition-all hover:scale-105 animate-fade-in-up delay-200"
          >
            Get started
            <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </section>

      {/* Analysis Section */}
      <section id="analyze" className="relative py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Semantic Code Analysis
            </h2>
            <p className="text-xl text-[#86868b] max-w-2xl mx-auto">
              Discover dependencies, understand structure, and map your entire codebase
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            {/* Analysis Card */}
            <div className="bg-white/5 backdrop-blur-2xl rounded-[28px] border border-white/10 overflow-hidden shadow-2xl">
              <div className="p-8 md:p-12">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-4 bg-blue-500/20 rounded-2xl">
                    <Code2 className="w-8 h-8 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-semibold text-white">Repository Path</h3>
                    <p className="text-sm text-[#86868b]">Enter the local path to your codebase</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <input
                    type="text"
                    value={repoPath}
                    onChange={(e) => setRepoPath(e.target.value)}
                    placeholder="/path/to/your/repository"
                    className="w-full px-6 py-5 bg-white/5 border border-white/10 rounded-2xl text-white text-lg placeholder-[#86868b] focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all"
                  />

                  {error && (
                    <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                      <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-red-300">{error}</p>
                    </div>
                  )}

                  <button
                    onClick={analyzeRepo}
                    disabled={analyzing || !repoPath.trim()}
                    className="w-full group relative px-6 py-5 bg-gradient-to-r from-blue-600 to-blue-500 rounded-2xl text-white font-semibold text-lg hover:from-blue-500 hover:to-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-[1.02] disabled:hover:scale-100"
                  >
                    <span className="flex items-center justify-center gap-3">
                      {analyzing ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Search className="w-5 h-5" />
                          Analyze Repository
                        </>
                      )}
                    </span>
                  </button>
                </div>

                {/* Stats Grid */}
                {stats && (
                  <div className="mt-8 pt-8 border-t border-white/10 grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-[#86868b]">
                        <FileCode className="w-4 h-4" />
                        <p className="text-sm">Files</p>
                      </div>
                      <p className="text-3xl font-bold text-white">{stats.files_parsed}</p>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-[#86868b]">
                        <Code2 className="w-4 h-4" />
                        <p className="text-sm">Functions</p>
                      </div>
                      <p className="text-3xl font-bold text-white">{stats.functions_found}</p>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-[#86868b]">
                        <GitBranch className="w-4 h-4" />
                        <p className="text-sm">Dependencies</p>
                      </div>
                      <p className="text-3xl font-bold text-white">{stats.edges_created}</p>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-[#86868b]">
                        <Clock className="w-4 h-4" />
                        <p className="text-sm">Time</p>
                      </div>
                      <p className="text-3xl font-bold text-white">{stats.time_taken_seconds.toFixed(1)}s</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Query Section */}
      <section id="query" className={`relative py-32 px-6 transition-opacity duration-500 ${analyzed ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
              AI-Powered Queries
            </h2>
            <p className="text-xl text-[#86868b] max-w-2xl mx-auto">
              Ask questions in natural language and get intelligent code insights
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="bg-white/5 backdrop-blur-2xl rounded-[28px] border border-white/10 overflow-hidden shadow-2xl">
              <div className="p-8 md:p-12">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-4 bg-green-500/20 rounded-2xl">
                    <Brain className="w-8 h-8 text-green-400" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-semibold text-white">Natural Language Query</h3>
                    <p className="text-sm text-[#86868b]">Ask about safety, impact, or code dependencies</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleQuery();
                      }
                    }}
                    placeholder="e.g., Is it safe to delete the payment processor?"
                    rows={3}
                    disabled={!analyzed}
                    className="w-full px-6 py-5 bg-white/5 border border-white/10 rounded-2xl text-white text-lg placeholder-[#86868b] focus:outline-none focus:border-green-500/50 focus:bg-white/10 transition-all resize-none"
                  />

                  <button
                    onClick={handleQuery}
                    disabled={queryLoading || !query.trim() || !analyzed}
                    className="w-full group relative px-6 py-5 bg-gradient-to-r from-green-600 to-green-500 rounded-2xl text-white font-semibold text-lg hover:from-green-500 hover:to-green-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-[1.02] disabled:hover:scale-100"
                  >
                    <span className="flex items-center justify-center gap-3">
                      {queryLoading ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-5 h-5" />
                          Ask AI
                        </>
                      )}
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AI Results Section */}
      {result && (
        <section className="relative py-32 px-6 bg-gradient-to-b from-black via-blue-950/10 to-black">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/30 mb-6">
                <CheckCircle2 className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400">Analysis Complete</span>
              </div>
              <h2 className="text-5xl md:text-6xl font-bold text-white mb-4">
                Intelligent Insights
              </h2>
              <p className="text-xl text-[#86868b]">AI-powered code understanding and risk assessment</p>
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Risk & Business Impact */}
              <div className="lg:col-span-2 space-y-6">
                {/* Risk Assessment Card */}
                <div className="bg-white/5 backdrop-blur-2xl rounded-[28px] border border-white/10 p-8 md:p-10">
                  <div className="flex items-start justify-between mb-8">
                    <div>
                      <h3 className="text-2xl font-semibold text-white mb-2">Risk Assessment</h3>
                      <code className="text-blue-400 font-mono text-lg">{result.extracted_function}</code>
                    </div>
                    <div className={`px-4 py-2 rounded-full border ${getRiskBg(result.analysis_result?.summary.risk_level || '')}`}>
                      <span className={`text-sm font-semibold uppercase ${getRiskColor(result.analysis_result?.summary.risk_level || '')}`}>
                        {result.analysis_result?.summary.risk_level}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-8">
                    <div>
                      <p className="text-sm text-[#86868b] mb-2">Risk Score</p>
                      <p className={`text-7xl font-bold ${getRiskColor(result.analysis_result?.summary.risk_level || '')}`}>
                        {result.analysis_result?.summary.risk_score}
                      </p>
                      <p className="text-sm text-[#86868b] mt-2">out of 100</p>
                    </div>
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <FileCode className="w-5 h-5 text-[#86868b]" />
                        <div>
                          <p className="text-2xl font-semibold text-white">{result.analysis_result?.summary.total_usages}</p>
                          <p className="text-xs text-[#86868b]">Total Usages</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Code2 className="w-5 h-5 text-[#86868b]" />
                        <div>
                          <p className="text-2xl font-semibold text-white">{result.analysis_result?.summary.total_files}</p>
                          <p className="text-xs text-[#86868b]">Files Affected</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {result.analysis_result?.safety_recommendation && (
                    <div className="mt-6 p-4 bg-white/5 rounded-2xl border border-white/10">
                      <p className="text-sm text-white">{result.analysis_result.safety_recommendation}</p>
                    </div>
                  )}
                </div>

                {/* Business Impact Card */}
                {result.analysis_result?.business_impact && (
                  <div className="bg-white/5 backdrop-blur-2xl rounded-[28px] border border-white/10 p-8 md:p-10">
                    <div className="flex items-center gap-3 mb-6">
                      <TrendingUp className="w-6 h-6 text-orange-400" />
                      <h3 className="text-2xl font-semibold text-white">Business Impact</h3>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="p-5 bg-white/5 rounded-2xl border border-white/10">
                        <div className="flex items-center gap-2 mb-3">
                          <DollarSign className="w-5 h-5 text-green-400" />
                          <p className="text-sm text-[#86868b]">Revenue Impact</p>
                        </div>
                        <p className="text-lg font-semibold text-white">{result.analysis_result.business_impact.revenue_impact_range}</p>
                      </div>
                      <div className="p-5 bg-white/5 rounded-2xl border border-white/10">
                        <div className="flex items-center gap-2 mb-3">
                          <Users className="w-5 h-5 text-blue-400" />
                          <p className="text-sm text-[#86868b]">Users Affected</p>
                        </div>
                        <p className="text-lg font-semibold text-white">{result.analysis_result.business_impact.affected_users}</p>
                      </div>
                      <div className="p-5 bg-white/5 rounded-2xl border border-white/10">
                        <div className="flex items-center gap-2 mb-3">
                          <Clock className="w-5 h-5 text-purple-400" />
                          <p className="text-sm text-[#86868b]">Recovery Time</p>
                        </div>
                        <p className="text-lg font-semibold text-white">{result.analysis_result.business_impact.estimated_recovery_time}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column - AI Understanding */}
              <div className="space-y-6">
                <div className="bg-white/5 backdrop-blur-2xl rounded-[28px] border border-white/10 p-8">
                  <div className="flex items-center gap-3 mb-6">
                    <Brain className="w-6 h-6 text-purple-400" />
                    <h3 className="text-2xl font-semibold text-white">AI Understanding</h3>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <p className="text-sm text-[#86868b] mb-2">Intent</p>
                      <p className="text-white leading-relaxed">{result.understood_intent}</p>
                    </div>

                    <div>
                      <p className="text-sm text-[#86868b] mb-2">Action</p>
                      <div className="inline-flex px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded-lg">
                        <span className="text-blue-400 font-mono text-sm">{result.extracted_action}</span>
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <p className="text-sm text-[#86868b]">Confidence</p>
                        <p className="text-2xl font-bold text-white">{(result.confidence * 100).toFixed(0)}%</p>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-1000"
                          style={{ width: `${result.confidence * 100}%` }}
                        />
                      </div>
                    </div>

                    <div className="p-4 bg-white/5 rounded-2xl border border-white/10">
                      <p className="text-sm text-[#86868b] italic leading-relaxed">"{result.ai_reasoning}"</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Affected Modules */}
            {result.analysis_result && result.analysis_result.modules.length > 0 && (
              <div className="mt-16">
                <h3 className="text-3xl font-bold text-white mb-8">Affected Modules</h3>
                <div className="grid grid-cols-1 gap-4">
                  {result.analysis_result.modules.map((mod, i) => (
                    <div key={i} className="group bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-6 hover:bg-white/10 transition-all">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            {getCriticalityIcon(mod.criticality)}
                            <h4 className="text-lg font-semibold text-white">{mod.module_name}</h4>
                          </div>
                          <p className="text-sm text-[#86868b] font-mono">{mod.file_path}</p>
                        </div>
                        <div className={`px-3 py-1 rounded-lg border ${getRiskBg(mod.criticality)}`}>
                          <span className={`text-xs font-semibold uppercase ${getRiskColor(mod.criticality)}`}>
                            {mod.criticality.replace('_', ' ')}
                          </span>
                        </div>
                      </div>

                      <p className="text-sm text-[#86868b] mb-4 leading-relaxed">{mod.impact_description}</p>

                      {mod.usages[0] && (
                        <div className="p-4 bg-black/40 rounded-xl border border-white/10">
                          <code className="text-sm text-green-400 font-mono break-all">{mod.usages[0].context}</code>
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
      <footer className="relative py-20 px-6 border-t border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-white" />
              <span className="text-xl font-semibold text-white">ReasonOS</span>
            </div>

            <div className="flex items-center gap-6 text-sm text-[#86868b]">
              <span>Powered by Gemini AI</span>
              <span>•</span>
              <span>Tree-sitter</span>
              <span>•</span>
              <span>NetworkX</span>
            </div>

            <div className="flex items-center gap-6 text-sm">
              <a href="https://github.com/Motupallisailohith/ReasonOS" target="_blank" rel="noopener noreferrer" className="text-[#86868b] hover:text-white transition-colors">
                GitHub
              </a>
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-[#86868b] hover:text-white transition-colors">
                API Docs
              </a>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-white/10 text-center">
            <p className="text-sm text-[#86868b]">
              Built with love for safer, smarter code refactoring
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
};

export default ModernUI;
