import {
  Brain,
  CheckCircle2,
  ChevronRight,
  Clock,
  Code2,
  FileCode,
  GitBranch,
  Search,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { ErrorAlert } from './components/reasonos/ErrorAlert';
import { GraphVisualization } from './components/reasonos/GraphVisualization';
import { LoadingSpinner } from './components/reasonos/LoadingSpinner';
import { ModuleCard } from './components/reasonos/ModuleCard';
import { StatCard } from './components/reasonos/StatCard';
import { reasonosAPI } from './services/reasonos-api';
import type { AnalysisStatistics, QueryResponse } from './types/schema';
import { formatNumber } from './utils/formatters';

function App() {
  const [repoPath, setRepoPath] = useState("C:\\Users\\sailo\\ReasonOS\\ReasonOS");
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [stats, setStats] = useState<AnalysisStatistics | null>(null);
  const [query, setQuery] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const analyzeRepo = async () => {
    if (!repoPath.trim()) return;

    setAnalyzing(true);
    setResult(null);
    setError('');

    try {
      console.log('Analyzing repository:', repoPath);
      const data = await reasonosAPI.analyzeRepository(repoPath);
      console.log('Analysis response:', data);
      setStats(data.statistics);
      setAnalyzed(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze repository');
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
      console.log('Querying repository:', repoPath);
      console.log('Query:', query);
      const data = await reasonosAPI.queryAI(repoPath, query);
      console.log('Query response:', data);
      setResult(data);

      // Scroll to results
      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }, 100);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process query';
      console.error('Query error details:', err);

      // If repository not found in backend cache, suggest re-analyzing
      if (errorMessage.includes('not analyzed') || errorMessage.includes('404')) {
        setError('Repository cache expired. Please click "Analyze" again to rebuild the graph, then retry your query.');
        setAnalyzed(false);
      } else {
        setError(errorMessage);
      }
    } finally {
      setQueryLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
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
            <a href="#analyze" className="text-[#86868b] hover:text-white transition-colors">
              Analyze
            </a>
            <a href="#query" className="text-[#86868b] hover:text-white transition-colors">
              Query
            </a>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#86868b] hover:text-white transition-colors"
            >
              Docs
            </a>
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
            ReasonOS uses semantic graphs and AI to analyze code dependencies, assess risks, and
            provide intelligent insights for safer refactoring.
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

                <div className="flex flex-col sm:flex-row items-center gap-4">
                  <div className="relative w-full">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#86868b]" />
                    <input
                      type="text"
                      value={repoPath}
                      onChange={(e) => setRepoPath(e.target.value)}
                      placeholder="e.g., /Users/user/project/my-repo"
                      className="w-full bg-black/20 border border-white/10 rounded-full py-4 pl-12 pr-4 text-white placeholder:text-[#86868b] focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                    />
                  </div>
                  <button
                    onClick={analyzeRepo}
                    disabled={analyzing}
                    className="w-full sm:w-auto flex-shrink-0 bg-blue-600 text-white font-semibold rounded-full px-8 py-4 hover:bg-blue-700 disabled:bg-blue-900/50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
                  >
                    {analyzing ? (
                      <>
                        <LoadingSpinner />
                        Analyzing...
                      </>
                    ) : (
                      'Analyze'
                    )}
                  </button>
                </div>
              </div>

              {analyzing && (
                <div className="p-8 md:p-12 border-t border-white/10">
                  <div className="flex flex-col items-center text-center">
                    <LoadingSpinner size="lg" />
                    <p className="mt-4 text-lg text-white">Analyzing codebase...</p>
                    <p className="text-sm text-[#86868b]">This might take a few moments for large repositories.</p>
                  </div>
                </div>
              )}

              {error && !analyzing && (
                <div className="p-8 md:p-12 border-t border-white/10">
                  <ErrorAlert message={error} />
                </div>
              )}

              {analyzed && stats && (
                <>
                  <div className="border-t border-white/10 p-8 md:p-12">
                    <h4 className="text-2xl font-semibold text-white mb-8 text-center">Analysis Complete</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                      <StatCard icon={FileCode} label="Files Discovered" value={formatNumber(stats.files_discovered)} />
                      <StatCard icon={Code2} label="Files Parsed" value={formatNumber(stats.files_parsed)} />
                      <StatCard icon={GitBranch} label="Functions Found" value={formatNumber(stats.functions_found)} />
                      <StatCard icon={Clock} label="Analysis Time" value={`${stats.time_taken_seconds.toFixed(2)}s`} />
                      <StatCard icon={CheckCircle2} label="Graph Edges" value={formatNumber(stats.edges_created)} />
                      <StatCard icon={TrendingUp} label="Graph Nodes" value={formatNumber(stats.graph_stats?.total_nodes || 0)} />
                    </div>
                  </div>

                  {/* Graph Visualization */}
                  <div className="border-t border-white/10 p-8 md:p-12">
                    <GraphVisualization repoPath={repoPath} maxNodes={50} />
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Query Section */}
      <section id="query" className="py-32 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Ask the AI
            </h2>
            <p className="text-xl text-[#86868b] max-w-2xl mx-auto">
              Query your codebase with natural language to get intelligent insights
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-2xl rounded-[28px] border border-white/10 p-8 md:p-12 shadow-2xl">
            <div className="flex items-center gap-4 mb-8">
              <div className="p-4 bg-purple-500/20 rounded-2xl">
                <Sparkles className="w-8 h-8 text-purple-400" />
              </div>
              <div>
                <h3 className="text-2xl font-semibold text-white">Natural Language Query</h3>
                <p className="text-sm text-[#86868b]">
                  {analyzed ? 'Ask about specific functions in your codebase.' : 'Analyze your repository to enable the query feature.'}
                </p>
              </div>
            </div>

            {analyzed && (
              <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                <p className="text-sm text-[#86868b] mb-2">💡 Example queries:</p>
                <div className="text-sm text-white space-y-1">
                  <div>• "What happens if I change analyzeRepo?"</div>
                  <div>• "Is it safe to refactor handleQuery?"</div>
                  <div>• "Show me usages of StatCard"</div>
                  <div>• "What would break if I rename App?"</div>
                </div>
              </div>
            )}

            <div className="flex flex-col sm:flex-row items-start gap-4">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  analyzed
                    ? "e.g., 'What happens if I change analyzeRepo?'"
                    : 'Please analyze a repository first...'
                }
                disabled={!analyzed || queryLoading}
                className="w-full h-24 sm:h-auto sm:min-h-[56px] resize-none bg-black/20 border border-white/10 rounded-2xl py-4 px-4 text-white placeholder:text-[#86868b] focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all disabled:opacity-50"
                rows={2}
              />
              <button
                onClick={handleQuery}
                disabled={!analyzed || queryLoading || !query.trim()}
                className="w-full sm:w-auto flex-shrink-0 bg-purple-600 text-white font-semibold rounded-full px-8 py-4 hover:bg-purple-700 disabled:bg-purple-900/50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
              >
                {queryLoading ? (
                  <>
                    <LoadingSpinner />
                    Thinking...
                  </>
                ) : (
                  'Query'
                )}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Results Section */}
      {result && (
        <section id="results" className="pb-32 px-6 animate-fade-in">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
                AI Response
              </h2>
            </div>

            <div className="bg-gradient-to-b from-white/5 to-transparent rounded-[28px] border border-white/10 p-8 md:p-12 shadow-2xl">
              {/* AI Understanding */}
              <div className="mb-12">
                <h3 className="text-3xl font-bold text-white mb-6">AI Understanding</h3>
                <div className="bg-black/20 p-6 rounded-xl space-y-4">
                  <div>
                    <span className="text-[#86868b]">Intent: </span>
                    <span className="text-white">{result.understood_intent}</span>
                  </div>
                  <div>
                    <span className="text-[#86868b]">Function: </span>
                    <span className="text-white font-mono">{result.extracted_function}</span>
                  </div>
                  <div>
                    <span className="text-[#86868b]">Action: </span>
                    <span className="text-white">{result.extracted_action}</span>
                  </div>
                  <div>
                    <span className="text-[#86868b]">Confidence: </span>
                    <span className="text-white">{(result.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div>
                    <span className="text-[#86868b]">AI Reasoning: </span>
                    <span className="text-[#d2d2d7]">{result.ai_reasoning}</span>
                  </div>
                </div>
              </div>

              {/* Summary */}
              {result.analysis_result?.summary && (
                <div className="mb-12">
                  <h3 className="text-3xl font-bold text-white mb-6">Analysis Summary</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6 bg-black/20 p-6 rounded-xl">
                    <div>
                      <p className="text-[#86868b] text-sm">Total Usages</p>
                      <p className="text-white text-2xl font-bold">{result.analysis_result.summary.total_usages}</p>
                    </div>
                    <div>
                      <p className="text-[#86868b] text-sm">Files Affected</p>
                      <p className="text-white text-2xl font-bold">{result.analysis_result.summary.total_files}</p>
                    </div>
                    <div>
                      <p className="text-[#86868b] text-sm">Risk Level</p>
                      <p className="text-white text-2xl font-bold">{result.analysis_result.summary.risk_level}</p>
                    </div>
                    <div>
                      <p className="text-[#86868b] text-sm">Risk Score</p>
                      <p className="text-white text-2xl font-bold">{result.analysis_result.summary.risk_score.toFixed(2)}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Safety Recommendation */}
              {result.analysis_result?.safety_recommendation && (
                <div className="mb-12">
                  <h3 className="text-3xl font-bold text-white mb-6">Safety Recommendation</h3>
                  <div className="bg-black/20 p-6 rounded-xl">
                    <p className="text-lg text-[#d2d2d7]">{result.analysis_result.safety_recommendation}</p>
                  </div>
                </div>
              )}

              {/* Business Impact */}
              {result.analysis_result?.business_impact && (
                <div className="mb-12">
                  <h3 className="text-3xl font-bold text-white mb-6">Business Impact</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-black/20 p-6 rounded-xl">
                    <div>
                      <p className="text-[#86868b] text-sm">Revenue Impact</p>
                      <p className="text-white text-lg font-semibold">{result.analysis_result.business_impact.revenue_impact_range}</p>
                    </div>
                    <div>
                      <p className="text-[#86868b] text-sm">Affected Users</p>
                      <p className="text-white text-lg font-semibold">{result.analysis_result.business_impact.affected_users}</p>
                    </div>
                    <div>
                      <p className="text-[#86868b] text-sm">Recovery Time</p>
                      <p className="text-white text-lg font-semibold">{result.analysis_result.business_impact.estimated_recovery_time}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Affected Modules */}
              {result.analysis_result?.modules && result.analysis_result.modules.length > 0 && (
                <div>
                  <h3 className="text-3xl font-bold text-white mb-6">Affected Modules</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {result.analysis_result.modules.map((mod) => (
                      <ModuleCard key={mod.module_name} module={mod} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-white/10 mt-20">
        <div className="max-w-7xl mx-auto px-6 py-12 text-center text-[#86868b]">
          <p>&copy; {new Date().getFullYear()} ReasonOS. All rights reserved.</p>
          <p className="mt-2 text-sm">
            An AI-powered semantic code analysis platform.
          </p>
        </div>
      </footer>
    </main>
  );
}

export default App;
