"""
Graph Builder
Builds dependency graph from parsed code
Stores in Neo4j or JSON

Implementation of STEP 3: BUILD GRAPH STRUCTURE
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from pathlib import Path

from .parser import ParsedFile, FunctionDefinition, FunctionCall, ImportStatement, ExportStatement


# ============================================================================
# STEP 3: GRAPH STRUCTURE (Nodes + Edges)
# ============================================================================

class NodeType(Enum):
    """Types of nodes in the graph"""
    FUNCTION = "function"
    CLASS = "class"
    FILE = "file"
    MODULE = "module"


class EdgeType(Enum):
    """Types of relationships between nodes"""
    CALLS = "calls"
    IMPORTS = "imports"
    EXPORTS = "exports"
    DEFINES = "defines"
    CONTAINED_IN = "contained_in"


@dataclass
class GraphNode:
    """
    Represents a code entity in the graph

    From specification STEP 3:
    Node 1: calculatePrice
    ├─ id: "calculatePrice"
    ├─ file: "checkout.js"
    ├─ line: 10
    ├─ type: "function"
    ├─ exported: true
    ├─ parameters: ["items"]
    └─ called_by_functions: ["processCheckout", "validatePayment", ...]
    """
    id: str  # Unique identifier (e.g., "checkout.js:calculatePrice")
    name: str  # Entity name (e.g., "calculatePrice")
    type: NodeType  # function, class, file, module
    file_path: str  # Source file
    line_number: int  # Line where defined
    end_line: int = 0

    # Function-specific
    parameters: List[str] = field(default_factory=list)
    is_exported: bool = False
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)

    # Relationships (populated during indexing)
    calls: List[str] = field(default_factory=list)  # Functions this calls
    called_by: List[str] = field(default_factory=list)  # Functions that call this
    imported_from: Optional[str] = None  # Source module if imported
    imported_in: List[str] = field(default_factory=list)  # Files that import this

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        data = asdict(self)
        data['type'] = self.type.value
        return data


@dataclass
class GraphEdge:
    """
    Represents a relationship between code entities

    From specification STEP 3:
    Edge 1: checkout.js → calls → calculatePrice (line 38)
    """
    id: str  # Unique edge ID
    source_id: str  # Source node ID
    target_id: str  # Target node ID
    edge_type: EdgeType  # calls, imports, exports, etc.

    # Context
    file_path: str  # Where relationship occurs
    line_number: int  # Line number
    context: Optional[str] = None  # Code context

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        data = asdict(self)
        data['edge_type'] = self.edge_type.value
        return data


@dataclass
class CodeGraph:
    """
    Complete dependency graph of a codebase

    Contains all nodes and edges extracted from parsing
    """
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[GraphEdge] = field(default_factory=list)

    # Statistics
    total_functions: int = 0
    total_files: int = 0
    total_calls: int = 0
    total_imports: int = 0

    def add_node(self, node: GraphNode):
        """Add a node to the graph"""
        self.nodes[node.id] = node
        if node.type == NodeType.FUNCTION:
            self.total_functions += 1
        elif node.type == NodeType.FILE:
            self.total_files += 1

    def add_edge(self, edge: GraphEdge):
        """Add an edge to the graph"""
        self.edges.append(edge)
        if edge.edge_type == EdgeType.CALLS:
            self.total_calls += 1
        elif edge.edge_type == EdgeType.IMPORTS:
            self.total_imports += 1

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'edges': [edge.to_dict() for edge in self.edges],
            'statistics': {
                'total_functions': self.total_functions,
                'total_files': self.total_files,
                'total_calls': self.total_calls,
                'total_imports': self.total_imports,
            }
        }


class GraphBuilder:
    """
    Builds dependency graph from parsed code files

    Implementation of STEP 3 from specification:
    - Create nodes for all code entities
    - Create edges for all relationships
    - Build complete graph structure
    - Store in Neo4j or JSON
    """

    def __init__(self, storage_type: str = "json"):
        """
        Initialize graph builder

        Args:
            storage_type: "json" for mock storage, "neo4j" for graph database
        """
        self.storage_type = storage_type
        self.graph = CodeGraph()
        self._function_map: Dict[str, str] = {}  # function_name -> node_id mapping

    def build_graph(self, parsed_files: List[ParsedFile]) -> CodeGraph:
        """
        Build complete dependency graph from parsed files

        Process from specification:
        1. Create nodes for all functions
        2. Create edges for all calls
        3. Create edges for all imports
        4. Link everything together

        Args:
            parsed_files: List of parsed code files

        Returns:
            Complete CodeGraph with all nodes and edges
        """
        # STEP 1: Create file nodes
        for parsed_file in parsed_files:
            self._create_file_node(parsed_file)

        # STEP 2: Create function nodes
        for parsed_file in parsed_files:
            self._create_function_nodes(parsed_file)

        # STEP 3: Create call edges
        for parsed_file in parsed_files:
            self._create_call_edges(parsed_file)

        # STEP 4: Create import edges
        for parsed_file in parsed_files:
            self._create_import_edges(parsed_file)

        # STEP 5: Create export edges
        for parsed_file in parsed_files:
            self._create_export_edges(parsed_file)

        # STEP 6: Build reverse relationships (called_by, imported_in)
        self._build_reverse_relationships()

        return self.graph

    def _create_file_node(self, parsed_file: ParsedFile):
        """Create a node for the file itself"""
        file_id = self._make_file_id(parsed_file.file_path)

        node = GraphNode(
            id=file_id,
            name=Path(parsed_file.file_path).name,
            type=NodeType.FILE,
            file_path=parsed_file.file_path,
            line_number=1
        )
        self.graph.add_node(node)

    def _create_function_nodes(self, parsed_file: ParsedFile):
        """
        Create nodes for all functions in a file

        Implementation of STEP 3 specification:
        Creates nodes like:
        Node 1: calculatePrice
        ├─ id: "calculatePrice"
        ├─ file: "checkout.js"
        ├─ line: 10
        └─ ...
        """
        for func_def in parsed_file.functions:
            # Create unique node ID
            node_id = self._make_function_id(func_def.file_path, func_def.name)

            node = GraphNode(
                id=node_id,
                name=func_def.name,
                type=NodeType.FUNCTION,
                file_path=func_def.file_path,
                line_number=func_def.line_number,
                end_line=func_def.end_line,
                parameters=func_def.parameters,
                is_exported=func_def.is_exported,
                is_async=func_def.is_async,
                decorators=func_def.decorators
            )

            self.graph.add_node(node)

            # Store mapping for quick lookup
            self._function_map[func_def.name] = node_id

            # Create edge from file to function (DEFINES relationship)
            file_id = self._make_file_id(func_def.file_path)
            edge = GraphEdge(
                id=f"{file_id}->defines->{node_id}",
                source_id=file_id,
                target_id=node_id,
                edge_type=EdgeType.DEFINES,
                file_path=func_def.file_path,
                line_number=func_def.line_number
            )
            self.graph.add_edge(edge)

    def _create_call_edges(self, parsed_file: ParsedFile):
        """
        Create edges for function calls

        Implementation of STEP 3 specification:
        Edge 1: checkout.js → calls → calculatePrice (line 38)
        """
        for call in parsed_file.calls:
            # Find source node (calling function)
            source_id = None
            if call.calling_function:
                source_id = self._make_function_id(call.file_path, call.calling_function)
            else:
                # Module-level call
                source_id = self._make_file_id(call.file_path)

            # Find target node (called function)
            target_id = self._resolve_function_id(call.function_name, call.file_path)

            if source_id and target_id:
                edge_id = f"{source_id}->calls->{target_id}@{call.line_number}"
                edge = GraphEdge(
                    id=edge_id,
                    source_id=source_id,
                    target_id=target_id,
                    edge_type=EdgeType.CALLS,
                    file_path=call.file_path,
                    line_number=call.line_number
                )
                self.graph.add_edge(edge)

                # Update node's calls list
                source_node = self.graph.get_node(source_id)
                if source_node and target_id not in source_node.calls:
                    source_node.calls.append(target_id)

    def _create_import_edges(self, parsed_file: ParsedFile):
        """
        Create edges for import statements

        Implementation of STEP 3 specification:
        Edge 3: payment.js → imports → calculatePrice (line 3)
        """
        file_id = self._make_file_id(parsed_file.file_path)

        for imp in parsed_file.imports:
            for imported_name in imp.imported_names:
                # Try to resolve the imported function
                target_id = self._resolve_imported_function(
                    imported_name,
                    imp.source_module,
                    parsed_file.file_path
                )

                if target_id:
                    edge_id = f"{file_id}->imports->{target_id}@{imp.line_number}"
                    edge = GraphEdge(
                        id=edge_id,
                        source_id=file_id,
                        target_id=target_id,
                        edge_type=EdgeType.IMPORTS,
                        file_path=parsed_file.file_path,
                        line_number=imp.line_number,
                        context=f"from {imp.source_module}"
                    )
                    self.graph.add_edge(edge)

    def _create_export_edges(self, parsed_file: ParsedFile):
        """Create edges for export statements"""
        file_id = self._make_file_id(parsed_file.file_path)

        for exp in parsed_file.exports:
            for exported_name in exp.exported_names:
                # Find the function being exported
                func_id = self._make_function_id(parsed_file.file_path, exported_name)

                if self.graph.get_node(func_id):
                    edge_id = f"{file_id}->exports->{func_id}@{exp.line_number}"
                    edge = GraphEdge(
                        id=edge_id,
                        source_id=file_id,
                        target_id=func_id,
                        edge_type=EdgeType.EXPORTS,
                        file_path=parsed_file.file_path,
                        line_number=exp.line_number
                    )
                    self.graph.add_edge(edge)

    def _build_reverse_relationships(self):
        """
        Build reverse relationships (called_by, imported_in)

        This enables fast lookups like:
        "Show me all functions that call calculatePrice"
        """
        for edge in self.graph.edges:
            if edge.edge_type == EdgeType.CALLS:
                # Add to target's called_by list
                target_node = self.graph.get_node(edge.target_id)
                if target_node and edge.source_id not in target_node.called_by:
                    target_node.called_by.append(edge.source_id)

            elif edge.edge_type == EdgeType.IMPORTS:
                # Add to target's imported_in list
                target_node = self.graph.get_node(edge.target_id)
                if target_node and edge.file_path not in target_node.imported_in:
                    target_node.imported_in.append(edge.file_path)

    # Helper methods for ID generation and resolution

    def _make_file_id(self, file_path: str) -> str:
        """Create unique ID for a file"""
        return f"file:{Path(file_path).name}"

    def _make_function_id(self, file_path: str, func_name: str) -> str:
        """Create unique ID for a function"""
        file_name = Path(file_path).stem
        return f"{file_name}:{func_name}"

    def _resolve_function_id(self, func_name: str, context_file: str) -> Optional[str]:
        """
        Resolve a function name to its node ID

        Tries:
        1. Same file
        2. Function map (global lookup)
        """
        # Try same file first
        local_id = self._make_function_id(context_file, func_name)
        if self.graph.get_node(local_id):
            return local_id

        # Try function map
        return self._function_map.get(func_name)

    def _resolve_imported_function(self, func_name: str, source_module: str,
                                   importing_file: str) -> Optional[str]:
        """
        Resolve an imported function to its node ID

        Handles relative imports like:
        - './checkout' -> checkout.js in same directory
        - '../lib/utils' -> utils.js in parent/lib
        """
        # Simple resolution - could be enhanced
        return self._function_map.get(func_name)

    def save_to_json(self, output_path: str):
        """Save graph to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(self.graph.to_dict(), f, indent=2)

    def save_to_neo4j(self, neo4j_uri: str, username: str, password: str):
        """Save graph to Neo4j database (TODO: implement)"""
        # TODO: Implement Neo4j storage
        raise NotImplementedError("Neo4j storage not yet implemented")
