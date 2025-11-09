"""
Semantic Graph Orchestrator
Main entry point for graph generation, impact analysis, and risk assessment

Complete implementation of STEPS 1-9 from specification
"""

from typing import Dict, List, Optional
from pathlib import Path
import time
import json

from .parser import FileDiscovery, CodeParser, FileInfo, ParsedFile
from .graph_builder import GraphBuilder, CodeGraph
from .analyzer import CodeAnalyzer, UsageReport
from .impact_analyzer import ImpactAnalyzer, ImpactReport
from .risk_calculator import RiskCalculator, RiskAssessment


class SemanticGraphOrchestrator:
    """
    Orchestrates the complete semantic graph pipeline

    Pipeline flow (from specification):
    1. File Discovery → Find all code files
    2. AST Parsing → Extract functions, calls, imports
    3. Graph Building → Create nodes and edges
    4. Indexing → Build fast lookup indexes
    5. Analysis → Query usages and dependencies
    6. Impact Assessment → Categorize by module and criticality
    7. Risk Calculation → Calculate risk scores
    8. Failure Analysis → Analyze failure modes

    Example usage:
        orchestrator = SemanticGraphOrchestrator("/path/to/repo")
        orchestrator.build_graph()
        impact = orchestrator.assess_change_impact("calculatePrice", "Rename to computeTotal")
        print(impact.to_dict())
    """

    def __init__(self, repository_path: str):
        """
        Initialize orchestrator

        Args:
            repository_path: Path to repository to analyze
        """
        self.repository_path = repository_path

        # Components (initialized after build_graph)
        self.file_discovery: Optional[FileDiscovery] = None
        self.parser: Optional[CodeParser] = None
        self.graph_builder: Optional[GraphBuilder] = None
        self.graph: Optional[CodeGraph] = None
        self.analyzer: Optional[CodeAnalyzer] = None
        self.impact_analyzer: Optional[ImpactAnalyzer] = None
        self.risk_calculator: Optional[RiskCalculator] = None

        # Statistics
        self.stats = {
            'files_discovered': 0,
            'files_parsed': 0,
            'functions_found': 0,
            'edges_created': 0,
            'time_taken_seconds': 0.0
        }

    def build_graph(self, storage_path: Optional[str] = None) -> CodeGraph:
        """
        Build complete semantic graph

        Runs STEPS 1-4 from specification:
        1. Discover files
        2. Parse files
        3. Build graph
        4. Create indexes

        Args:
            storage_path: Optional path to save graph JSON

        Returns:
            Complete CodeGraph with indexes
        """
        start_time = time.time()

        print(f"🔍 Building semantic graph for: {self.repository_path}")
        print("=" * 70)

        # STEP 1: File Discovery
        print("\n📂 STEP 1: Discovering code files...")
        discovered_files = self._discover_files()
        self.stats['files_discovered'] = len(discovered_files)
        print(f"   ✓ Found {len(discovered_files)} code files")

        # STEP 2: Parse Files
        print("\n🌲 STEP 2: Parsing files with Tree-sitter...")
        parsed_files = self._parse_files(discovered_files)
        self.stats['files_parsed'] = len(parsed_files)
        functions_count = sum(len(pf.functions) for pf in parsed_files)
        self.stats['functions_found'] = functions_count
        print(f"   ✓ Parsed {len(parsed_files)} files")
        print(f"   ✓ Extracted {functions_count} functions")

        # STEP 3: Build Graph
        print("\n🕸️  STEP 3: Building dependency graph...")
        self.graph = self._build_graph(parsed_files)
        self.stats['edges_created'] = len(self.graph.edges)
        print(f"   ✓ Created {len(self.graph.nodes)} nodes")
        print(f"   ✓ Created {len(self.graph.edges)} edges")

        # STEP 4: Create Indexes
        print("\n📊 STEP 4: Creating fast lookup indexes...")
        self._create_indexes()
        print(f"   ✓ Indexed {len(self.analyzer.indexes.function_usages)} functions")

        # Save to storage if requested
        if storage_path:
            print(f"\n💾 Saving graph to: {storage_path}")
            self.graph_builder.save_to_json(storage_path)
            print(f"   ✓ Graph saved")

        # Complete
        end_time = time.time()
        self.stats['time_taken_seconds'] = round(end_time - start_time, 2)

        print("\n" + "=" * 70)
        print(f"✅ Graph built successfully in {self.stats['time_taken_seconds']}s")
        self._print_statistics()

        return self.graph

    def _discover_files(self) -> List[FileInfo]:
        """STEP 1: Discover all code files"""
        self.file_discovery = FileDiscovery(self.repository_path)
        files = self.file_discovery.discover_files()

        # Print statistics
        stats = self.file_discovery.get_statistics(files)
        for file_type, count in stats['by_type'].items():
            print(f"   • {file_type}: {count} files")

        return files

    def _parse_files(self, files: List[FileInfo]) -> List[ParsedFile]:
        """STEP 2: Parse all files with Tree-sitter"""
        self.parser = CodeParser()
        parsed_files = []

        for i, file_info in enumerate(files, 1):
            if i % 10 == 0:  # Progress update every 10 files
                print(f"   Parsing file {i}/{len(files)}...")

            parsed_file = self.parser.parse_file(file_info)
            parsed_files.append(parsed_file)

            if parsed_file.parse_errors:
                print(f"   ⚠️  Errors in {file_info.relative_path}: {parsed_file.parse_errors}")

        return parsed_files

    def _build_graph(self, parsed_files: List[ParsedFile]) -> CodeGraph:
        """STEP 3: Build graph from parsed files"""
        self.graph_builder = GraphBuilder(storage_type="json")
        graph = self.graph_builder.build_graph(parsed_files)
        return graph

    def _create_indexes(self):
        """STEP 4: Create fast lookup indexes"""
        self.analyzer = CodeAnalyzer(self.graph)
        self.analyzer.create_indexes()

        # Initialize impact analyzer and risk calculator
        self.impact_analyzer = ImpactAnalyzer(self.analyzer)
        self.risk_calculator = RiskCalculator()

    def _print_statistics(self):
        """Print summary statistics"""
        print("\n📈 Summary:")
        print(f"   • Files discovered: {self.stats['files_discovered']}")
        print(f"   • Files parsed: {self.stats['files_parsed']}")
        print(f"   • Functions found: {self.stats['functions_found']}")
        print(f"   • Graph nodes: {len(self.graph.nodes)}")
        print(f"   • Graph edges: {self.stats['edges_created']}")
        print(f"   • Time taken: {self.stats['time_taken_seconds']}s")

    # ========================================================================
    # QUERY METHODS (STEPS 5-9)
    # ========================================================================

    def find_usages(self, function_name: str) -> Optional[UsageReport]:
        """
        Find all usages of a function

        Implementation of STEP 5 & 7 from specification:
        Returns complete usage report with:
        - Definition location
        - Export statements
        - Import statements
        - All function calls
        - Test references

        Args:
            function_name: Name of function to find

        Returns:
            UsageReport with all locations
        """
        if not self.analyzer:
            raise RuntimeError("Graph not built. Call build_graph() first.")

        return self.analyzer.find_all_usages(function_name)

    def assess_change_impact(self, function_name: str,
                            change_description: str = "") -> Optional[ImpactReport]:
        """
        Assess complete impact of changing a function

        Implementation of STEPS 6-9 from specification:
        - Find all usages
        - Categorize by module
        - Assign criticality levels
        - Calculate risk score
        - Assess business impact

        Args:
            function_name: Name of function being changed
            change_description: Description of change (e.g., "Rename to computeTotal")

        Returns:
            ImpactReport with complete assessment

        Example:
            impact = orchestrator.assess_change_impact(
                "calculatePrice",
                "Rename to computeTotal"
            )
            print(f"Risk Level: {impact.risk_score.risk_level.value}")
            print(f"Total Usages: {impact.total_usages}")
            print(f"Risk Score: {impact.risk_score.total_score}")
        """
        if not self.impact_analyzer:
            raise RuntimeError("Graph not built. Call build_graph() first.")

        return self.impact_analyzer.assess_change_impact(
            function_name,
            change_description
        )

    def calculate_risk(self, function_name: str,
                      change_type: str = "rename") -> RiskAssessment:
        """
        Calculate failure modes and risk

        Implementation of STEP 9c from specification:
        - Analyze 5 failure modes
        - Calculate probabilities
        - Generate mitigation strategies
        - Estimate success rate

        Args:
            function_name: Name of function
            change_type: Type of change (rename, refactor, delete)

        Returns:
            RiskAssessment with failure mode analysis
        """
        if not self.risk_calculator:
            raise RuntimeError("Graph not built. Call build_graph() first.")

        return self.risk_calculator.calculate_failure_modes(
            function_name,
            change_type
        )

    def get_complete_analysis(self, function_name: str,
                             change_description: str = "Refactor") -> Dict:
        """
        Get complete analysis combining all components

        Returns:
            - Usage report (STEP 5, 7)
            - Impact assessment (STEP 6-9)
            - Risk analysis (STEP 9c)

        This is the main method for comprehensive analysis
        """
        if not self.analyzer:
            raise RuntimeError("Graph not built. Call build_graph() first.")

        print(f"\n🔬 Analyzing impact of changing: {function_name}")
        print("=" * 70)

        # Get usage report
        print("\n📍 Finding all usages...")
        usage_report = self.find_usages(function_name)
        if not usage_report:
            return {'error': f'Function not found: {function_name}'}

        print(f"   ✓ Found {usage_report.total_usages} usages across {len(usage_report.files_affected)} files")

        # Get impact assessment
        print("\n⚠️  Assessing impact...")
        impact_report = self.assess_change_impact(function_name, change_description)
        if impact_report:
            print(f"   ✓ Risk Level: {impact_report.risk_score.risk_level.value.upper()}")
            print(f"   ✓ Risk Score: {impact_report.risk_score.total_score} points")
            print(f"   ✓ Modules Affected: {len(impact_report.modules)}")

        # Get risk analysis
        print("\n🎯 Calculating failure modes...")
        risk_assessment = self.calculate_risk(function_name, "rename")
        print(f"   ✓ Success Rate: {risk_assessment.success_rate_percent}%")
        print(f"   ✓ Failure Modes Analyzed: {len(risk_assessment.failure_modes)}")

        print("\n" + "=" * 70)
        print("✅ Analysis complete\n")

        # Combine everything
        return {
            'function_name': function_name,
            'change_description': change_description,
            'usage_report': usage_report.to_dict() if usage_report else None,
            'impact_assessment': impact_report.to_dict() if impact_report else None,
            'risk_analysis': risk_assessment.to_dict(),
            'statistics': self.stats
        }

    def export_analysis(self, function_name: str, output_path: str):
        """
        Export complete analysis to JSON file

        Args:
            function_name: Function to analyze
            output_path: Path to save JSON report
        """
        analysis = self.get_complete_analysis(function_name)

        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"📄 Analysis exported to: {output_path}")

    def get_statistics(self) -> Dict:
        """Get pipeline statistics"""
        return {
            **self.stats,
            'graph_stats': self.graph.to_dict()['statistics'] if self.graph else {}
        }


# ============================================================================
# CLI / Quick Usage Functions
# ============================================================================

def analyze_repository(repo_path: str, output_dir: str = None) -> SemanticGraphOrchestrator:
    """
    Quick function to analyze a repository

    Args:
        repo_path: Path to repository
        output_dir: Optional directory to save outputs

    Returns:
        Configured orchestrator ready for queries
    """
    orchestrator = SemanticGraphOrchestrator(repo_path)

    # Build graph
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        graph_path = str(Path(output_dir) / "code_graph.json")
    else:
        graph_path = None

    orchestrator.build_graph(storage_path=graph_path)

    return orchestrator


def analyze_function_change(repo_path: str, function_name: str,
                           change_description: str = "Refactor",
                           output_path: str = None) -> Dict:
    """
    Quick function to analyze impact of changing a function

    Args:
        repo_path: Path to repository
        function_name: Function to analyze
        change_description: What change is being made
        output_path: Optional path to save report

    Returns:
        Complete analysis dictionary
    """
    orchestrator = analyze_repository(repo_path)
    analysis = orchestrator.get_complete_analysis(function_name, change_description)

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"📄 Report saved to: {output_path}")

    return analysis
