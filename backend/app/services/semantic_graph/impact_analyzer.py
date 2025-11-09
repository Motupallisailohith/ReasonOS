"""
Impact Analyzer
Assesses the impact and risk of code changes

Implementation of STEP 6, 7, 8:
- Categorize usages by module and criticality
- Calculate risk scores
- Assess business impact
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from pathlib import Path

from .analyzer import CodeAnalyzer, UsageReport, UsageLocation, UsageType


# ============================================================================
# STEP 6: MODULE CATEGORIZATION & CRITICALITY
# ============================================================================

class CriticalityLevel(Enum):
    """
    Criticality levels for code modules

    From specification STEP 6:
    - CRITICAL_PATH: Core business logic (checkout, payment)
    - SECONDARY: Important but not critical (invoices, utilities)
    - TERTIARY: Nice-to-have (validation, helpers)
    - NON_CRITICAL: Tests, dev tools
    """
    CRITICAL_PATH = "critical_path"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    NON_CRITICAL = "non_critical"


class RiskLevel(Enum):
    """
    Risk levels for changes

    From specification STEP 7:
    0-20 points: LOW
    21-50 points: MEDIUM
    51-100 points: HIGH
    101+ points: CRITICAL
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ModuleUsage:
    """
    Usages grouped by module with criticality

    From specification STEP 8:
    CHECKOUT MODULE (checkout.js):
    ├─ Definition: 1 location (line 10)
    ├─ Export: 1 location (line 1)
    ├─ Calls: 3 locations (lines 38, 40, ...)
    ├─ Risk: 🔴 HIGH
    └─ Criticality: CRITICAL_PATH
    """
    module_name: str
    file_path: str
    criticality: CriticalityLevel

    # Usage counts
    definition_count: int = 0
    export_count: int = 0
    import_count: int = 0
    call_count: int = 0

    # Detailed locations
    usages: List[UsageLocation] = field(default_factory=list)

    # Risk assessment
    risk_description: str = ""
    impact_description: str = ""

    def total_usages(self) -> int:
        """Total number of usages in this module"""
        return len(self.usages)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'module_name': self.module_name,
            'file_path': self.file_path,
            'criticality': self.criticality.value,
            'usage_counts': {
                'definition': self.definition_count,
                'export': self.export_count,
                'import': self.import_count,
                'call': self.call_count,
                'total': self.total_usages()
            },
            'risk_description': self.risk_description,
            'impact_description': self.impact_description,
            'usages': [u.to_dict() for u in self.usages]
        }


@dataclass
class RiskScore:
    """
    Calculated risk score for a change

    From specification STEP 9:
    RISK_SCORE = (Critical×10) + (Secondary×5) + (Tertiary×2) + (NonCritical×1)
    """
    # Usage counts by criticality
    critical_path_usages: int = 0
    secondary_usages: int = 0
    tertiary_usages: int = 0
    non_critical_usages: int = 0

    # Calculated score
    total_score: int = 0
    risk_level: RiskLevel = RiskLevel.LOW

    # Breakdown
    critical_points: int = 0
    secondary_points: int = 0
    tertiary_points: int = 0
    non_critical_points: int = 0

    def calculate(self):
        """
        Calculate risk score using specification formula

        Formula from STEP 9:
        Risk_Score = (Critical_Usages × 10) + (Secondary_Usages × 5) +
                     (Tertiary_Usages × 2) + (Non_Critical × 1)
        """
        self.critical_points = self.critical_path_usages * 10
        self.secondary_points = self.secondary_usages * 5
        self.tertiary_points = self.tertiary_usages * 2
        self.non_critical_points = self.non_critical_usages * 1

        self.total_score = (
            self.critical_points +
            self.secondary_points +
            self.tertiary_points +
            self.non_critical_points
        )

        # Map score to risk level
        if self.total_score >= 101:
            self.risk_level = RiskLevel.CRITICAL
        elif self.total_score >= 51:
            self.risk_level = RiskLevel.HIGH
        elif self.total_score >= 21:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'total_score': self.total_score,
            'risk_level': self.risk_level.value,
            'breakdown': {
                'critical_path': {
                    'usages': self.critical_path_usages,
                    'points': self.critical_points,
                    'weight': 10
                },
                'secondary': {
                    'usages': self.secondary_usages,
                    'points': self.secondary_points,
                    'weight': 5
                },
                'tertiary': {
                    'usages': self.tertiary_usages,
                    'points': self.tertiary_points,
                    'weight': 2
                },
                'non_critical': {
                    'usages': self.non_critical_usages,
                    'points': self.non_critical_points,
                    'weight': 1
                }
            },
            'formula': '(Critical×10) + (Secondary×5) + (Tertiary×2) + (NonCritical×1)'
        }


@dataclass
class ImpactReport:
    """
    Complete impact assessment report for a code change

    Implementation of complete STEP 6-9 output
    """
    function_name: str
    change_description: str

    # Module breakdown
    modules: List[ModuleUsage] = field(default_factory=list)

    # Risk assessment
    risk_score: RiskScore = field(default_factory=RiskScore)

    # Business impact
    revenue_impact_low: str = ""
    revenue_impact_high: str = ""
    affected_users: str = ""
    recovery_time: str = ""

    # Totals
    total_usages: int = 0
    total_files: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'function_name': self.function_name,
            'change_description': self.change_description,
            'summary': {
                'total_usages': self.total_usages,
                'total_files': self.total_files,
                'risk_level': self.risk_score.risk_level.value,
                'risk_score': self.risk_score.total_score
            },
            'risk_score': self.risk_score.to_dict(),
            'modules': [m.to_dict() for m in self.modules],
            'business_impact': {
                'revenue_impact_range': f"{self.revenue_impact_low} - {self.revenue_impact_high}",
                'affected_users': self.affected_users,
                'estimated_recovery_time': self.recovery_time
            }
        }


# ============================================================================
# IMPACT ANALYZER
# ============================================================================

class ImpactAnalyzer:
    """
    Analyzes impact and risk of code changes

    Implementation of STEP 6, 7, 8, 9 from specification:
    - Categorize usages by module and criticality
    - Calculate risk scores
    - Assess business impact
    - Generate complete impact reports
    """

    # Module patterns and their criticality levels
    # These would typically come from configuration
    MODULE_PATTERNS = {
        'checkout': CriticalityLevel.CRITICAL_PATH,
        'payment': CriticalityLevel.CRITICAL_PATH,
        'auth': CriticalityLevel.CRITICAL_PATH,
        'billing': CriticalityLevel.CRITICAL_PATH,

        'invoice': CriticalityLevel.SECONDARY,
        'report': CriticalityLevel.SECONDARY,
        'email': CriticalityLevel.SECONDARY,
        'notification': CriticalityLevel.SECONDARY,

        'util': CriticalityLevel.TERTIARY,
        'helper': CriticalityLevel.TERTIARY,
        'validate': CriticalityLevel.TERTIARY,
        'format': CriticalityLevel.TERTIARY,

        'test': CriticalityLevel.NON_CRITICAL,
        'spec': CriticalityLevel.NON_CRITICAL,
        'mock': CriticalityLevel.NON_CRITICAL,
        'fixture': CriticalityLevel.NON_CRITICAL,
    }

    def __init__(self, analyzer: CodeAnalyzer):
        """
        Initialize impact analyzer

        Args:
            analyzer: CodeAnalyzer with built indexes
        """
        self.analyzer = analyzer

    def assess_change_impact(self, function_name: str,
                            change_description: str = "") -> Optional[ImpactReport]:
        """
        Assess the complete impact of changing a function

        Implementation of STEP 6-9:
        1. Get all usages
        2. Categorize by module
        3. Assign criticality levels
        4. Calculate risk score
        5. Assess business impact

        Args:
            function_name: Name of function being changed
            change_description: Description of the change (e.g., "Rename to computeTotal")

        Returns:
            ImpactReport with complete assessment
        """
        # Get all usages
        usage_report = self.analyzer.find_all_usages(function_name)
        if not usage_report:
            return None

        # Create impact report
        report = ImpactReport(
            function_name=function_name,
            change_description=change_description,
            total_usages=usage_report.total_usages,
            total_files=len(usage_report.files_affected)
        )

        # STEP 6: Categorize by module
        modules = self._categorize_by_module(usage_report)
        report.modules = modules

        # STEP 7: Calculate risk score
        risk_score = self._calculate_risk_score(modules)
        report.risk_score = risk_score

        # STEP 8 & 9: Assess business impact
        self._assess_business_impact(report, modules, risk_score)

        return report

    def _categorize_by_module(self, usage_report: UsageReport) -> List[ModuleUsage]:
        """
        Categorize usages by module and assign criticality

        Implementation of STEP 8 from specification:
        Groups usages by file/module and assigns criticality level
        """
        # Group by file
        modules_by_file: Dict[str, List[UsageLocation]] = defaultdict(list)

        # Add all usages to appropriate file
        if usage_report.definition:
            modules_by_file[usage_report.definition.file_path].append(usage_report.definition)

        for usage_list in [usage_report.exports, usage_report.imports,
                          usage_report.calls, usage_report.tests]:
            for usage in usage_list:
                modules_by_file[usage.file_path].append(usage)

        # Create ModuleUsage objects
        modules = []
        for file_path, usages in modules_by_file.items():
            module = self._create_module_usage(file_path, usages)
            modules.append(module)

        # Sort by criticality (most critical first)
        criticality_order = {
            CriticalityLevel.CRITICAL_PATH: 0,
            CriticalityLevel.SECONDARY: 1,
            CriticalityLevel.TERTIARY: 2,
            CriticalityLevel.NON_CRITICAL: 3
        }
        modules.sort(key=lambda m: criticality_order[m.criticality])

        return modules

    def _create_module_usage(self, file_path: str,
                            usages: List[UsageLocation]) -> ModuleUsage:
        """
        Create ModuleUsage object for a file

        Determines criticality based on file path patterns
        """
        # Determine module name and criticality
        file_name = Path(file_path).stem
        criticality = self._determine_criticality(file_path, file_name)

        # Count usage types
        definition_count = sum(1 for u in usages if u.usage_type == UsageType.DEFINITION)
        export_count = sum(1 for u in usages if u.usage_type == UsageType.EXPORT)
        import_count = sum(1 for u in usages if u.usage_type == UsageType.IMPORT)
        call_count = sum(1 for u in usages if u.usage_type == UsageType.CALL)

        # Generate risk and impact descriptions
        risk_desc = self._generate_risk_description(criticality, file_name, len(usages))
        impact_desc = self._generate_impact_description(criticality, file_name)

        return ModuleUsage(
            module_name=file_name.upper() + " MODULE",
            file_path=file_path,
            criticality=criticality,
            definition_count=definition_count,
            export_count=export_count,
            import_count=import_count,
            call_count=call_count,
            usages=usages,
            risk_description=risk_desc,
            impact_description=impact_desc
        )

    def _determine_criticality(self, file_path: str, file_name: str) -> CriticalityLevel:
        """
        Determine criticality level based on file path/name

        Uses MODULE_PATTERNS to classify modules
        """
        file_path_lower = file_path.lower()
        file_name_lower = file_name.lower()

        # Check patterns
        for pattern, criticality in self.MODULE_PATTERNS.items():
            if pattern in file_path_lower or pattern in file_name_lower:
                return criticality

        # Default to SECONDARY for unknown modules
        return CriticalityLevel.SECONDARY

    def _generate_risk_description(self, criticality: CriticalityLevel,
                                   module_name: str, usage_count: int) -> str:
        """Generate risk description based on criticality"""
        if criticality == CriticalityLevel.CRITICAL_PATH:
            return f"🔴 HIGH - Core {module_name} logic. If broken: Users can't complete transactions. Impact: Revenue loss"
        elif criticality == CriticalityLevel.SECONDARY:
            return f"🟡 MEDIUM - {module_name} functionality. If broken: Feature degradation. Impact: User experience affected"
        elif criticality == CriticalityLevel.TERTIARY:
            return f"🟢 LOW - Helper {module_name}. If broken: Minor issues. Impact: Edge cases affected"
        else:
            return f"⚪ NONE - {module_name} (tests/dev). If broken: No user impact. Impact: Development only"

    def _generate_impact_description(self, criticality: CriticalityLevel,
                                    module_name: str) -> str:
        """Generate business impact description"""
        if criticality == CriticalityLevel.CRITICAL_PATH:
            return "ALL users affected. Transactions blocked. Revenue loss: $50K-$500K/hour"
        elif criticality == CriticalityLevel.SECONDARY:
            return "Some users affected. Feature unavailable. Business impact: moderate"
        elif criticality == CriticalityLevel.TERTIARY:
            return "Few users affected. Edge case failures. Business impact: minimal"
        else:
            return "Developers affected. No customer impact."

    def _calculate_risk_score(self, modules: List[ModuleUsage]) -> RiskScore:
        """
        Calculate risk score using specification formula

        Implementation of STEP 9:
        Risk_Score = (Critical×10) + (Secondary×5) + (Tertiary×2) + (NonCritical×1)
        """
        score = RiskScore()

        # Count usages by criticality
        for module in modules:
            usage_count = module.total_usages()

            if module.criticality == CriticalityLevel.CRITICAL_PATH:
                score.critical_path_usages += usage_count
            elif module.criticality == CriticalityLevel.SECONDARY:
                score.secondary_usages += usage_count
            elif module.criticality == CriticalityLevel.TERTIARY:
                score.tertiary_usages += usage_count
            else:
                score.non_critical_usages += usage_count

        # Calculate score
        score.calculate()

        return score

    def _assess_business_impact(self, report: ImpactReport,
                               modules: List[ModuleUsage],
                               risk_score: RiskScore):
        """
        Assess business impact

        Implementation of STEP 9b from specification
        """
        # Count critical modules
        critical_modules = [m for m in modules
                          if m.criticality == CriticalityLevel.CRITICAL_PATH]

        if critical_modules:
            # High impact
            report.revenue_impact_low = "$50K/hour"
            report.revenue_impact_high = "$500K/hour"
            report.affected_users = "ALL users (100% of transactions)"
            report.recovery_time = "3-6 hours"
        elif risk_score.risk_level == RiskLevel.HIGH:
            # Medium-high impact
            report.revenue_impact_low = "$10K/hour"
            report.revenue_impact_high = "$100K/hour"
            report.affected_users = "Many users (30-70% of transactions)"
            report.recovery_time = "1-3 hours"
        elif risk_score.risk_level == RiskLevel.MEDIUM:
            # Medium impact
            report.revenue_impact_low = "$1K/hour"
            report.revenue_impact_high = "$20K/hour"
            report.affected_users = "Some users (10-30% of transactions)"
            report.recovery_time = "0.5-2 hours"
        else:
            # Low impact
            report.revenue_impact_low = "$0/hour"
            report.revenue_impact_high = "$5K/hour"
            report.affected_users = "Few users or developers only"
            report.recovery_time = "0.5-1 hour"
