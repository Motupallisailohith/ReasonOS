// Mock data for ReasonOS UI

import { RiskLevel, CriticalityLevel } from '../types/enums';
import type { AnalyzeResponse, QueryResponse } from '../types/schema';

// API response data
export const mockQuery = {
  analyzeResponse: {
    status: "success",
    message: "Analyzed repository: 47 files, 234 functions",
    statistics: {
      files_discovered: 47,
      files_parsed: 47,
      functions_found: 234,
      edges_created: 892,
      time_taken_seconds: 3.42
    },
    graph_id: "C:\\Users\\sailo\\ReasonOS\\ReasonOS"
  } as AnalyzeResponse,
  
  queryResponse: {
    understood_intent: "Analyze safety_check impact for 'runTransaction'",
    extracted_function: "runTransaction",
    extracted_action: "safety_check",
    confidence: 0.95,
    ai_reasoning: "User is asking about the safety of deleting/modifying the runTransaction function. This requires a comprehensive impact assessment to determine risk level.",
    analysis_result: {
      function_name: "runTransaction",
      change_description: "Safety check for modification",
      summary: {
        total_usages: 47,
        total_files: 12,
        risk_level: RiskLevel.HIGH,
        risk_score: 0.78
      },
      risk_score: {
        risk_level: RiskLevel.HIGH,
        risk_score: 0.78,
        factors: {
          usage_frequency: 0.8,
          criticality_score: 0.85,
          test_coverage: 0.6
        }
      },
      modules: [
        {
          module_name: "Payment Processing",
          file_path: "backend/app/services/payment/processor.py",
          criticality: CriticalityLevel.CRITICAL,
          impact_description: "Core payment transaction handling - directly affects revenue",
          usages: [
            { line: 145, context: "result = runTransaction(payment_data, user_id)" },
            { line: 289, context: "await runTransaction(refund_params)" }
          ]
        },
        {
          module_name: "Order Management",
          file_path: "backend/app/services/orders/manager.py",
          criticality: CriticalityLevel.HIGH,
          impact_description: "Order completion and fulfillment workflows",
          usages: [
            { line: 67, context: "transaction_id = runTransaction(order.total)" },
            { line: 234, context: "if runTransaction(checkout_data):" }
          ]
        },
        {
          module_name: "Subscription Service",
          file_path: "backend/app/services/subscriptions/billing.py",
          criticality: CriticalityLevel.HIGH,
          impact_description: "Recurring billing and subscription renewals",
          usages: [
            { line: 112, context: "runTransaction(subscription.amount, user)" }
          ]
        }
      ],
      business_impact: {
        revenue_impact_range: "$50K - $500K per hour",
        affected_users: "All active customers (~10,000 users)",
        estimated_recovery_time: "2-4 hours"
      },
      safety_recommendation: "⚠️ CAUTION: Requires careful review and testing"
    }
  } as QueryResponse
};

// Root component props
export const mockRootProps = {
  defaultRepoPath: "C:\\Users\\sailo\\ReasonOS\\ReasonOS",
  apiBaseUrl: "http://localhost:8000/api/v1"
};