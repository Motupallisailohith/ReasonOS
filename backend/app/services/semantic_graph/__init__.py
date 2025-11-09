"""
Layer 1: Semantic Graph Service

Complete implementation of Graph Generation, Impact Assessment, and Risk Analysis

Main entry point:
    from semantic_graph import SemanticGraphOrchestrator

    orchestrator = SemanticGraphOrchestrator("/path/to/repo")
    orchestrator.build_graph()
    impact = orchestrator.assess_change_impact("functionName")
"""

from .orchestrator import (
    SemanticGraphOrchestrator,
    analyze_repository,
    analyze_function_change
)

from .parser import (
    FileDiscovery,
    CodeParser,
    FileInfo,
    FileType,
    FunctionDefinition,
    FunctionCall,
    ImportStatement,
    ExportStatement,
    ParsedFile
)

from .graph_builder import (
    GraphBuilder,
    CodeGraph,
    GraphNode,
    GraphEdge,
    NodeType,
    EdgeType
)

from .analyzer import (
    CodeAnalyzer,
    UsageReport,
    UsageLocation,
    UsageType,
    GraphIndexes
)

from .impact_analyzer import (
    ImpactAnalyzer,
    ImpactReport,
    ModuleUsage,
    RiskScore,
    CriticalityLevel,
    RiskLevel
)

from .risk_calculator import (
    RiskCalculator,
    RiskAssessment,
    FailureModeAnalysis,
    FailureMode,
    MitigationStrategy
)

__all__ = [
    # Main orchestrator
    'SemanticGraphOrchestrator',
    'analyze_repository',
    'analyze_function_change',

    # Parser
    'FileDiscovery',
    'CodeParser',
    'FileInfo',
    'FileType',
    'FunctionDefinition',
    'FunctionCall',
    'ImportStatement',
    'ExportStatement',
    'ParsedFile',

    # Graph builder
    'GraphBuilder',
    'CodeGraph',
    'GraphNode',
    'GraphEdge',
    'NodeType',
    'EdgeType',

    # Analyzer
    'CodeAnalyzer',
    'UsageReport',
    'UsageLocation',
    'UsageType',
    'GraphIndexes',

    # Impact analyzer
    'ImpactAnalyzer',
    'ImpactReport',
    'ModuleUsage',
    'RiskScore',
    'CriticalityLevel',
    'RiskLevel',

    # Risk calculator
    'RiskCalculator',
    'RiskAssessment',
    'FailureModeAnalysis',
    'FailureMode',
    'MitigationStrategy',
]
