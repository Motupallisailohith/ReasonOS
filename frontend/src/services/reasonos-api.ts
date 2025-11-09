// API service for ReasonOS backend

import type { AnalyzeResponse, QueryResponse } from '../types/schema';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const reasonosAPI = {
  async analyzeRepository(repoPath: string, forceRebuild = false): Promise<AnalyzeResponse> {
    const response = await fetch(`${API_BASE_URL}/graph/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_path: repoPath, force_rebuild: forceRebuild }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Analysis failed');
    }

    return response.json();
  },

  async queryAI(repoPath: string, prompt: string, useAI = true): Promise<QueryResponse> {
    const response = await fetch(`${API_BASE_URL}/graph/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_path: repoPath, prompt, use_ai: useAI }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Query failed');
    }

    return response.json();
  },

  async exportGraphDOT(repoPath: string, maxNodes = 100, focusFunction?: string): Promise<{ format: string; content: string; metadata: any }> {
    const params = new URLSearchParams({
      repo_path: repoPath,
      max_nodes: maxNodes.toString(),
    });
    if (focusFunction) {
      params.append('focus_function', focusFunction);
    }

    const response = await fetch(`${API_BASE_URL}/graph/export/dot?${params}`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'DOT export failed');
    }

    return response.json();
  },
};
