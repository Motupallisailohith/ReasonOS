"""
Risk Calculator
Calculates failure modes and mitigation strategies

Implementation of STEP 9c: FAILURE MODE ANALYSIS
"""

from typing import Dict, List
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# STEP 9c: FAILURE MODE ANALYSIS
# ============================================================================

class FailureMode(Enum):
    """Types of failure modes"""
    MISSED_USAGE = "missed_usage"
    INCONSISTENT_RENAME = "inconsistent_rename"
    TYPE_MISMATCH = "type_mismatch"
    TEST_FAILURE = "test_failure"
    DOCUMENTATION_SYNC = "documentation_sync"


class DetectionMethod(Enum):
    """How failures are detected"""
    SEMANTIC_GRAPH = "semantic_graph"
    TYPE_CHECKER = "type_checker"
    TESTS = "tests"
    BUILD_SYSTEM = "build_system"
    MANUAL_REVIEW = "manual_review"


@dataclass
class FailureModeAnalysis:
    """
    Analysis of a specific failure mode

    From specification STEP 9c:
    FAILURE MODE 1: Missed a usage location
    ├─ Probability: LOW (0.01%) with semantic graph
    ├─ Impact: Code breaks at that location
    ├─ Symptom: Runtime error "calculatePrice is not defined"
    ├─ Detection: Tests fail
    └─ Recovery: Manual fix (30 min)
    """
    mode: FailureMode
    name: str

    # Risk assessment
    probability_percent: float
    probability_label: str  # "LOW", "MEDIUM", "HIGH"

    # Impact details
    impact_description: str
    symptom: str
    detection_method: DetectionMethod
    recovery_time_minutes: int

    # With/without mitigation
    probability_with_graph: float = 0.01  # With semantic graph
    probability_without_graph: float = 30.0  # Without (e.g., Copilot alone)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'mode': self.mode.value,
            'name': self.name,
            'probability': {
                'percent': self.probability_percent,
                'label': self.probability_label,
                'with_semantic_graph': self.probability_with_graph,
                'without_semantic_graph': self.probability_without_graph,
                'improvement': f"{self.probability_without_graph / self.probability_with_graph:.0f}x safer"
            },
            'impact': {
                'description': self.impact_description,
                'symptom': self.symptom,
                'detection': self.detection_method.value,
                'recovery_time': f"{self.recovery_time_minutes} minutes"
            }
        }


@dataclass
class MitigationStrategy:
    """Mitigation strategy for a failure mode"""
    failure_mode: FailureMode
    strategy: str
    effectiveness_percent: float

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'failure_mode': self.failure_mode.value,
            'strategy': self.strategy,
            'effectiveness': f"{self.effectiveness_percent}%"
        }


@dataclass
class RiskAssessment:
    """
    Complete risk assessment with failure modes

    Implementation of STEP 9c complete output
    """
    function_name: str
    change_type: str  # "rename", "refactor", "delete", etc.

    # Failure modes
    failure_modes: List[FailureModeAnalysis] = field(default_factory=list)

    # Mitigations
    mitigations: List[MitigationStrategy] = field(default_factory=list)

    # Overall success rate
    success_rate_percent: float = 99.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'function_name': self.function_name,
            'change_type': self.change_type,
            'overall_success_rate': f"{self.success_rate_percent}%",
            'failure_modes': [fm.to_dict() for fm in self.failure_modes],
            'mitigations': [m.to_dict() for m in self.mitigations],
            'summary': {
                'total_failure_modes': len(self.failure_modes),
                'high_risk_modes': sum(1 for fm in self.failure_modes
                                      if fm.probability_label == "HIGH"),
                'medium_risk_modes': sum(1 for fm in self.failure_modes
                                        if fm.probability_label == "MEDIUM"),
                'low_risk_modes': sum(1 for fm in self.failure_modes
                                     if fm.probability_label == "LOW")
            }
        }


class RiskCalculator:
    """
    Calculates risk and failure modes for code changes

    Implementation of STEP 9c from specification:
    - Analyze potential failure modes
    - Calculate probabilities
    - Generate mitigation strategies
    - Estimate overall success rate
    """

    def calculate_failure_modes(self, function_name: str,
                               change_type: str = "rename") -> RiskAssessment:
        """
        Calculate all failure modes for a change

        Implementation of STEP 9c from specification:
        Returns analysis of 5 failure modes with probabilities,
        impacts, and mitigation strategies

        Args:
            function_name: Name of function being changed
            change_type: Type of change (rename, refactor, delete)

        Returns:
            RiskAssessment with complete failure mode analysis
        """
        assessment = RiskAssessment(
            function_name=function_name,
            change_type=change_type
        )

        # Analyze each failure mode
        assessment.failure_modes = [
            self._analyze_missed_usage(),
            self._analyze_inconsistent_rename(),
            self._analyze_type_mismatch(),
            self._analyze_test_failure(),
            self._analyze_documentation_sync()
        ]

        # Generate mitigations
        assessment.mitigations = self._generate_mitigations()

        # Calculate overall success rate
        assessment.success_rate_percent = self._calculate_success_rate(
            assessment.failure_modes
        )

        return assessment

    def _analyze_missed_usage(self) -> FailureModeAnalysis:
        """
        Analyze FAILURE MODE 1: Missed a usage location

        From specification:
        Probability: LOW (0.01%) with semantic graph (30% with Copilot)
        Impact: Code breaks at that location
        Symptom: Runtime error "function is not defined"
        Detection: Tests fail
        Recovery: Manual fix (30 min)
        """
        return FailureModeAnalysis(
            mode=FailureMode.MISSED_USAGE,
            name="Missed a usage location",
            probability_percent=0.01,
            probability_label="LOW",
            probability_with_graph=0.01,
            probability_without_graph=30.0,
            impact_description="Code breaks at that location",
            symptom='Runtime error "function is not defined"',
            detection_method=DetectionMethod.TESTS,
            recovery_time_minutes=30
        )

    def _analyze_inconsistent_rename(self) -> FailureModeAnalysis:
        """
        Analyze FAILURE MODE 2: Inconsistent renaming

        From specification:
        Probability: LOW (0.05%)
        Impact: Some files renamed, others not
        Symptom: "function is not defined" in some modules
        Detection: Tests fail immediately
        Recovery: Rollback (2 min)
        """
        return FailureModeAnalysis(
            mode=FailureMode.INCONSISTENT_RENAME,
            name="Inconsistent renaming",
            probability_percent=0.05,
            probability_label="LOW",
            impact_description="Some files renamed, others not",
            symptom='"function is not defined" in some modules',
            detection_method=DetectionMethod.TESTS,
            recovery_time_minutes=2
        )

    def _analyze_type_mismatch(self) -> FailureModeAnalysis:
        """
        Analyze FAILURE MODE 3: Type system mismatch

        From specification:
        Probability: MEDIUM (2%) if TypeScript
        Impact: Type checker reports errors
        Symptom: "function is not assigned to type X"
        Detection: Build fails before deployment
        Recovery: Fix type definitions (30 min)
        """
        return FailureModeAnalysis(
            mode=FailureMode.TYPE_MISMATCH,
            name="Type system mismatch",
            probability_percent=2.0,
            probability_label="MEDIUM",
            impact_description="Type checker reports errors",
            symptom='"function is not assigned to type X"',
            detection_method=DetectionMethod.TYPE_CHECKER,
            recovery_time_minutes=30
        )

    def _analyze_test_failure(self) -> FailureModeAnalysis:
        """
        Analyze FAILURE MODE 4: Test expectations wrong

        From specification:
        Probability: LOW (0.5%)
        Impact: Tests reference old function name
        Symptom: "function is not defined" in tests
        Detection: Tests fail immediately
        Recovery: Manual fix (10 min)
        """
        return FailureModeAnalysis(
            mode=FailureMode.TEST_FAILURE,
            name="Test expectations wrong",
            probability_percent=0.5,
            probability_label="LOW",
            impact_description="Tests reference old function name",
            symptom='"function is not defined" in tests',
            detection_method=DetectionMethod.TESTS,
            recovery_time_minutes=10
        )

    def _analyze_documentation_sync(self) -> FailureModeAnalysis:
        """
        Analyze FAILURE MODE 5: Documentation out of sync

        From specification:
        Probability: HIGH (50%)
        Impact: Documentation still references old name
        Symptom: Developer confusion
        Detection: Manual review
        Recovery: Update docs (30 min)
        """
        return FailureModeAnalysis(
            mode=FailureMode.DOCUMENTATION_SYNC,
            name="Documentation out of sync",
            probability_percent=50.0,
            probability_label="HIGH",
            impact_description="Documentation still references old name",
            symptom="Developer confusion",
            detection_method=DetectionMethod.MANUAL_REVIEW,
            recovery_time_minutes=30
        )

    def _generate_mitigations(self) -> List[MitigationStrategy]:
        """
        Generate mitigation strategies

        From specification STEP 9c:
        MITIGATION:
        ├─ Use semantic graph: Catches modes 1, 2
        ├─ Validation layer: Catches mode 3
        ├─ Test execution: Catches modes 1, 2, 4
        ├─ Approval process: Catches mode 5
        └─ Combined: 99% success rate
        """
        return [
            MitigationStrategy(
                failure_mode=FailureMode.MISSED_USAGE,
                strategy="Use semantic graph to find ALL usages before changing",
                effectiveness_percent=99.99
            ),
            MitigationStrategy(
                failure_mode=FailureMode.INCONSISTENT_RENAME,
                strategy="Semantic graph ensures all locations updated atomically",
                effectiveness_percent=99.95
            ),
            MitigationStrategy(
                failure_mode=FailureMode.TYPE_MISMATCH,
                strategy="Run TypeScript type checker before deployment",
                effectiveness_percent=98.0
            ),
            MitigationStrategy(
                failure_mode=FailureMode.TEST_FAILURE,
                strategy="Execute full test suite in sandbox before approval",
                effectiveness_percent=99.5
            ),
            MitigationStrategy(
                failure_mode=FailureMode.DOCUMENTATION_SYNC,
                strategy="Human approval process reviews docs during code review",
                effectiveness_percent=50.0
            )
        ]

    def _calculate_success_rate(self, failure_modes: List[FailureModeAnalysis]) -> float:
        """
        Calculate overall success rate

        Success rate = 100% - sum(failure probabilities)
        Note: This is simplified; real calculation would use compound probability
        """
        # Use only technical failure modes (exclude documentation)
        technical_modes = [fm for fm in failure_modes
                          if fm.mode != FailureMode.DOCUMENTATION_SYNC]

        total_failure_probability = sum(fm.probability_percent for fm in technical_modes)
        success_rate = 100.0 - total_failure_probability

        return round(success_rate, 2)

    def estimate_revenue_impact(self, risk_level: str,
                               downtime_hours: float = 1.0) -> Dict:
        """
        Estimate revenue impact of a failure

        From specification STEP 9b:
        TOTAL IMPACT IF CHANGE BREAKS:
        ├─ Worst case: $100K/hour (payment system fails)
        ├─ Best case: $10K/hour (discounts fail)
        ├─ Average case: ~$50K/hour (partial breakage)
        └─ Typical incident recovery: 3-6 hours
        """
        if risk_level == "critical":
            hourly_low = 100_000
            hourly_high = 500_000
        elif risk_level == "high":
            hourly_low = 50_000
            hourly_high = 100_000
        elif risk_level == "medium":
            hourly_low = 10_000
            hourly_high = 50_000
        else:
            hourly_low = 0
            hourly_high = 10_000

        total_low = hourly_low * downtime_hours
        total_high = hourly_high * downtime_hours

        return {
            'hourly_impact': {
                'low': f"${hourly_low:,}/hour",
                'high': f"${hourly_high:,}/hour"
            },
            'total_potential_loss': {
                'low': f"${total_low:,}",
                'high': f"${total_high:,}",
                'downtime_hours': downtime_hours
            },
            'recovery_estimate': "3-6 hours typical"
        }

    def get_mitigation_strategies(self) -> List[str]:
        """
        Get list of all mitigation strategies

        Returns actionable steps to reduce risk
        """
        return [
            "✅ Use semantic graph analysis to identify ALL usages",
            "✅ Run full test suite in sandbox before deployment",
            "✅ Execute TypeScript type checker to catch type errors",
            "✅ Require human approval for high-risk changes",
            "✅ Update documentation as part of code review",
            "✅ Have rollback plan ready (< 2 minute recovery)",
            "✅ Monitor production for errors after deployment",
            "✅ Use feature flags for gradual rollout"
        ]
