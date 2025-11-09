// String formatting utilities for ReasonOS UI

import { RiskLevel, CriticalityLevel } from '../types/enums';

export const formatNumber = (num: number): string => {
  return num.toLocaleString();
};

export const formatTime = (seconds: number): string => {
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(0)}ms`;
  }
  return `${seconds.toFixed(2)}s`;
};

export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(0)}%`;
};

export const formatRiskLevel = (level: RiskLevel): string => {
  const labels = {
    [RiskLevel.CRITICAL]: "⛔ CRITICAL",
    [RiskLevel.HIGH]: "⚠️ HIGH",
    [RiskLevel.MEDIUM]: "⚡ MEDIUM",
    [RiskLevel.LOW]: "✓ LOW"
  };
  return labels[level] || level;
};

export const formatCriticality = (level: CriticalityLevel): string => {
  return level.charAt(0).toUpperCase() + level.slice(1).toLowerCase();
};