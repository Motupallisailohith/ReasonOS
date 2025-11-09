"""
Code Analyzer
Finds references, dependencies, call chains

Implementation of STEP 4 & 5:
- Create indexes for fast lookups
- Query graph for usage information
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from .graph_builder import CodeGraph, GraphNode, GraphEdge, EdgeType, NodeType


# ============================================================================
# STEP 4: GRAPH INDEXES FOR FAST LOOKUP
# ============================================================================

@dataclass
class GraphIndexes:
    """
    Fast lookup indexes for the code graph

    Implementation of STEP 4 specification:
    INDEX 1: Function Name → All Usage Locations
    INDEX 2: File → All Functions in That File
    INDEX 3: Function → Functions It Calls
    INDEX 4: Function → Functions That Call It
    """
    # INDEX 1: Function → All Usages (definition, export, import, calls)
    function_usages: Dict[str, List['UsageLocation']] = field(default_factory=lambda: defaultdict(list))

    # INDEX 2: File → Functions defined in that file
    file_functions: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))

    # INDEX 3: Function → Functions it calls
    function_calls: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))

    # INDEX 4: Function → Functions that call it
    function_called_by: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))

    # Additional useful indexes
    exported_functions: Dict[str, str] = field(default_factory=dict)  # name → node_id
    imported_functions: Dict[str, List[Tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))  # name → [(file, line)]


class UsageType(Enum):
    """Types of usage locations"""
    DEFINITION = "definition"
    EXPORT = "export"
    IMPORT = "import"
    CALL = "call"
    TEST = "test"


@dataclass
class UsageLocation:
    """
    Represents a location where a function is used

    From specification STEP 4:
    {
        type: "call",
        file: "payment.js",
        line: 12,
        context: "const expected = calculatePrice(items);"
    }
    """
    usage_type: UsageType
    file_path: str
    line_number: int
    context: str  # Code snippet showing usage
    containing_function: Optional[str] = None  # Function that contains this usage

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'type': self.usage_type.value,
            'file': self.file_path,
            'line': self.line_number,
            'context': self.context,
            'containing_function': self.containing_function
        }


# ============================================================================
# STEP 5: USAGE QUERY SYSTEM
# ============================================================================

@dataclass
class UsageReport:
    """
    Complete report of all usages of a function

    From specification STEP 7:
    Shows EVERYWHERE a function is used with:
    - Definition location
    - Export statements
    - Import statements
    - Function calls
    - Test references
    """
    function_name: str
    node_id: str

    # Breakdown by usage type
    definition: Optional[UsageLocation] = None
    exports: List[UsageLocation] = field(default_factory=list)
    imports: List[UsageLocation] = field(default_factory=list)
    calls: List[UsageLocation] = field(default_factory=list)
    tests: List[UsageLocation] = field(default_factory=list)

    # Summary counts
    total_usages: int = 0
    files_affected: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'function_name': self.function_name,
            'node_id': self.node_id,
            'total_usages': self.total_usages,
            'files_affected': list(self.files_affected),
            'breakdown': {
                'definition': self.definition.to_dict() if self.definition else None,
                'exports': [e.to_dict() for e in self.exports],
                'imports': [i.to_dict() for i in self.imports],
                'calls': [c.to_dict() for c in self.calls],
                'tests': [t.to_dict() for t in self.tests],
            },
            'summary': {
                'definition_count': 1 if self.definition else 0,
                'export_count': len(self.exports),
                'import_count': len(self.imports),
                'call_count': len(self.calls),
                'test_count': len(self.tests),
            }
        }


class CodeAnalyzer:
    """
    Analyzes code graph and provides fast queries

    Implementation of STEP 4 & 5 from specification:
    - Build indexes for O(1) lookups
    - Query for all usages of a function
    - Find dependencies and reverse dependencies
    """

    def __init__(self, graph: CodeGraph):
        """
        Initialize analyzer with code graph

        Args:
            graph: CodeGraph built from parsed files
        """
        self.graph = graph
        self.indexes = GraphIndexes()
        self._source_code_cache: Dict[str, List[str]] = {}  # file → lines

    def create_indexes(self):
        """
        Build all indexes for fast lookup

        Implementation of STEP 4 specification:
        Creates 4 main indexes for O(1) lookup time
        """
        print("Building graph indexes...")

        # INDEX 2: File → Functions
        self._build_file_functions_index()

        # INDEX 3 & 4: Function calls and reverse
        self._build_call_indexes()

        # INDEX 1: Function → All Usages (most complex)
        self._build_usage_index()

        # Build export/import indexes
        self._build_export_import_indexes()

        print(f"Indexes built: {len(self.indexes.function_usages)} functions indexed")

    def _build_file_functions_index(self):
        """Build INDEX 2: File → Functions in that file"""
        for node_id, node in self.graph.nodes.items():
            if node.type == NodeType.FUNCTION:
                file_name = node.file_path
                self.indexes.file_functions[file_name].append(node_id)

    def _build_call_indexes(self):
        """Build INDEX 3 & 4: Function calls and reverse"""
        for edge in self.graph.edges:
            if edge.edge_type == EdgeType.CALLS:
                # INDEX 3: source calls target
                self.indexes.function_calls[edge.source_id].append(edge.target_id)

                # INDEX 4: target is called by source
                self.indexes.function_called_by[edge.target_id].append(edge.source_id)

    def _build_usage_index(self):
        """
        Build INDEX 1: Function → All Usage Locations

        From specification STEP 4:
        "calculatePrice" → [
            { type: "definition", file: "checkout.js", line: 10, ... },
            { type: "export", file: "checkout.js", line: 1, ... },
            { type: "import", file: "payment.js", line: 3, ... },
            { type: "call", file: "payment.js", line: 12, ... },
            ...
        ]
        Total: 47 USAGES INDEXED
        """
        for node_id, node in self.graph.nodes.items():
            if node.type == NodeType.FUNCTION:
                usages = []

                # 1. DEFINITION location
                definition_usage = UsageLocation(
                    usage_type=UsageType.DEFINITION,
                    file_path=node.file_path,
                    line_number=node.line_number,
                    context=self._get_code_context(node.file_path, node.line_number)
                )
                usages.append(definition_usage)

                # 2. EXPORT locations (from edges)
                for edge in self.graph.edges:
                    if edge.target_id == node_id and edge.edge_type == EdgeType.EXPORTS:
                        export_usage = UsageLocation(
                            usage_type=UsageType.EXPORT,
                            file_path=edge.file_path,
                            line_number=edge.line_number,
                            context=self._get_code_context(edge.file_path, edge.line_number)
                        )
                        usages.append(export_usage)

                # 3. IMPORT locations
                for import_file in node.imported_in:
                    # Find import edges
                    for edge in self.graph.edges:
                        if (edge.target_id == node_id and
                            edge.edge_type == EdgeType.IMPORTS and
                            edge.file_path == import_file):
                            import_usage = UsageLocation(
                                usage_type=UsageType.IMPORT,
                                file_path=edge.file_path,
                                line_number=edge.line_number,
                                context=self._get_code_context(edge.file_path, edge.line_number)
                            )
                            usages.append(import_usage)

                # 4. CALL locations
                for edge in self.graph.edges:
                    if edge.target_id == node_id and edge.edge_type == EdgeType.CALLS:
                        # Get containing function
                        source_node = self.graph.get_node(edge.source_id)
                        containing_func = source_node.name if source_node else None

                        # Check if it's a test file
                        is_test = 'test' in edge.file_path.lower()
                        usage_type = UsageType.TEST if is_test else UsageType.CALL

                        call_usage = UsageLocation(
                            usage_type=usage_type,
                            file_path=edge.file_path,
                            line_number=edge.line_number,
                            context=self._get_code_context(edge.file_path, edge.line_number),
                            containing_function=containing_func
                        )
                        usages.append(call_usage)

                # Store in INDEX 1
                self.indexes.function_usages[node.name] = usages
                self.indexes.function_usages[node_id] = usages

    def _build_export_import_indexes(self):
        """Build export and import indexes"""
        for node_id, node in self.graph.nodes.items():
            if node.type == NodeType.FUNCTION and node.is_exported:
                self.indexes.exported_functions[node.name] = node_id

    def _get_code_context(self, file_path: str, line_number: int,
                         lines_before: int = 0, lines_after: int = 0) -> str:
        """
        Get code context around a line

        Returns the actual code snippet for display
        """
        # Load file into cache if not already there
        if file_path not in self._source_code_cache:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._source_code_cache[file_path] = f.readlines()
            except Exception:
                return ""

        lines = self._source_code_cache[file_path]

        # Get line range (1-indexed to 0-indexed)
        start_idx = max(0, line_number - 1 - lines_before)
        end_idx = min(len(lines), line_number + lines_after)

        # Get context lines
        context_lines = lines[start_idx:end_idx]
        return ''.join(context_lines).strip()

    # ========================================================================
    # QUERY METHODS (STEP 5 Implementation)
    # ========================================================================

    def find_all_usages(self, function_name: str) -> Optional[UsageReport]:
        """
        Find all usages of a function

        Implementation of STEP 7 from specification:
        QUERY: "Show me EVERYWHERE calculatePrice is used"
        Returns: 47 LOCATIONS with full details

        Args:
            function_name: Name of function to find usages for

        Returns:
            UsageReport with complete breakdown
        """
        # Look up in INDEX 1
        usages = self.indexes.function_usages.get(function_name)
        if not usages:
            return None

        # Create report
        report = UsageReport(
            function_name=function_name,
            node_id=self._get_node_id_by_name(function_name) or ""
        )

        # Categorize usages
        for usage in usages:
            if usage.usage_type == UsageType.DEFINITION:
                report.definition = usage
            elif usage.usage_type == UsageType.EXPORT:
                report.exports.append(usage)
            elif usage.usage_type == UsageType.IMPORT:
                report.imports.append(usage)
            elif usage.usage_type == UsageType.CALL:
                report.calls.append(usage)
            elif usage.usage_type == UsageType.TEST:
                report.tests.append(usage)

            # Track file
            report.files_affected.add(usage.file_path)

        # Calculate total
        report.total_usages = len(usages)

        return report

    def get_callers(self, function_name: str) -> List[str]:
        """
        Get all functions that call this function

        Uses INDEX 4: Function → Functions That Call It

        Args:
            function_name: Name of function

        Returns:
            List of function IDs that call this function
        """
        node_id = self._get_node_id_by_name(function_name)
        if not node_id:
            return []

        return self.indexes.function_called_by.get(node_id, [])

    def get_calls(self, function_name: str) -> List[str]:
        """
        Get all functions called by this function

        Uses INDEX 3: Function → Functions It Calls

        Args:
            function_name: Name of function

        Returns:
            List of function IDs called by this function
        """
        node_id = self._get_node_id_by_name(function_name)
        if not node_id:
            return []

        return self.indexes.function_calls.get(node_id, [])

    def get_function_details(self, function_name: str) -> Optional[GraphNode]:
        """Get full details of a function"""
        node_id = self._get_node_id_by_name(function_name)
        if not node_id:
            return None
        return self.graph.get_node(node_id)

    def get_functions_in_file(self, file_path: str) -> List[str]:
        """
        Get all functions defined in a file

        Uses INDEX 2: File → Functions
        """
        return self.indexes.file_functions.get(file_path, [])

    def _get_node_id_by_name(self, function_name: str) -> Optional[str]:
        """Helper to get node ID from function name"""
        return self.indexes.exported_functions.get(function_name)
