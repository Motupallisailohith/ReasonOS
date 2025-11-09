// Type definitions for ReasonOS UI

// Type definitions for ReasonOS UI

// Enums matching backend
export type RiskLevel = 'Low' | 'Medium' | 'High' | 'Critical' | 'Unknown';
export type CriticalityLevel = 'Low' | 'Medium' | 'High' | 'Critical';

// API Response types from the backend orchestrator and AI agent

export interface AnalysisStatistics {
  files_discovered: number;
  files_parsed: number;
  functions_found: number;
  edges_created: number;
  time_taken_seconds: number;
  graph_stats?: {
    total_nodes: number;
    total_edges: number;
  };
}

export interface AnalyzeResponse {
  status: string;
  message: string;
  statistics: AnalysisStatistics;
  graph_id: string;
}

export interface CodeUsage {
  line: number;
  context: string;
}

export interface AffectedModule {
  module_name: string;
  file_path: string;
  criticality: CriticalityLevel;
  impact_description: string;
  usages: CodeUsage[];
}

export interface Risk {
  category: string;
  level: RiskLevel;
  description: string;
  file_path?: string;
}

export interface CostAnalysis {
  estimated_cost_usd: number;
  required_expertise: string;
  assumptions: string;
}

export interface QueryResponse {
  understood_intent: string;
  extracted_function: string;
  extracted_action: string;
  confidence: number;
  ai_reasoning: string;
  analysis_result: {
    function_name: string;
    change_description?: string;
    summary: {
      total_usages: number;
      total_files: number;
      risk_level: RiskLevel;
      risk_score: number;
    };
    risk_score: {
      risk_level: RiskLevel;
      risk_score: number;
      factors?: {
        usage_frequency: number;
        criticality_score: number;
        test_coverage: number;
      };
    };
    modules: AffectedModule[];
    business_impact: {
      revenue_impact_range: string;
      affected_users: string;
      estimated_recovery_time: string;
    };
    safety_recommendation?: string;
  };
}
