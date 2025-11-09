"""
Code Parser using Tree-sitter
Extracts functions, classes, imports from source code
"""

import os
from pathlib import Path
from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
from tree_sitter import Language, Parser, Node


# ============================================================================
# STEP 1: FILE DISCOVERY SYSTEM
# ============================================================================

class FileType(Enum):
    """Supported file types for parsing"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JSX = "jsx"
    TSX = "tsx"


@dataclass
class FileInfo:
    """Information about a discovered code file"""
    path: str
    relative_path: str
    file_type: FileType
    size_bytes: int
    lines: int = 0


class FileDiscovery:
    """
    Discovers code files in a repository

    Implementation of STEP 1a & 1b from specification:
    - Walk directory tree
    - Filter code files by extension
    - Skip ignored patterns (node_modules, .git, etc.)
    - Return list of valid file paths
    """

    # Patterns to ignore (STEP 1b specification)
    IGNORED_DIRS = {
        'node_modules',
        '.git',
        '.github',
        'build',
        'dist',
        '.next',
        'venv',
        '.venv',
        'env',
        '__pycache__',
        '.pytest_cache',
        '.mypy_cache',
        'coverage',
        '.idea',
        '.vscode',
        'vendor',
        'target',
        'out',
    }

    # File extensions to process (STEP 1b specification)
    FILE_EXTENSIONS = {
        '.py': FileType.PYTHON,
        '.js': FileType.JAVASCRIPT,
        '.jsx': FileType.JSX,
        '.ts': FileType.TYPESCRIPT,
        '.tsx': FileType.TSX,
    }

    def __init__(self, root_path: str):
        """
        Initialize file discovery

        Args:
            root_path: Root directory to scan (e.g., "./my-project")
        """
        self.root_path = Path(root_path).resolve()
        if not self.root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")
        if not self.root_path.is_dir():
            raise ValueError(f"Path is not a directory: {root_path}")

    def discover_files(self) -> List[FileInfo]:
        """
        Walk directory tree and discover all code files

        Returns:
            List of FileInfo objects for each discovered file

        Example output (from specification):
            [
                FileInfo(path="./my-project/checkout.js", ...),
                FileInfo(path="./my-project/payment.js", ...),
                FileInfo(path="./my-project/invoice.js", ...),
                ...
            ]
        """
        discovered_files = []

        # Walk directory tree (STEP 1a)
        for root, dirs, files in os.walk(self.root_path):
            # Remove ignored directories in-place (modifies dirs during iteration)
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]

            # Process each file
            for filename in files:
                file_path = Path(root) / filename

                # Check if it's a code file we should process
                if self._is_code_file(filename):
                    file_info = self._create_file_info(file_path)
                    if file_info:
                        discovered_files.append(file_info)

        return discovered_files

    def _should_ignore_dir(self, dirname: str) -> bool:
        """
        Check if directory should be ignored

        Implementation of STEP 1b: Skip ignored patterns
        """
        return dirname in self.IGNORED_DIRS or dirname.startswith('.')

    def _is_code_file(self, filename: str) -> bool:
        """
        Check if file is a code file we should parse

        Implementation of STEP 1b: Check extension
        """
        return Path(filename).suffix in self.FILE_EXTENSIONS

    def _create_file_info(self, file_path: Path) -> Optional[FileInfo]:
        """
        Create FileInfo object for a discovered file

        Performs STEP 1b checks:
        ✓ Does file exist?
        ✓ Can we read it?
        ✓ Is it a code file?
        """
        try:
            # Check file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                return None

            # Get file type from extension
            suffix = file_path.suffix
            file_type = self.FILE_EXTENSIONS.get(suffix)
            if not file_type:
                return None

            # Get file size
            size_bytes = file_path.stat().st_size

            # Count lines (for statistics)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = sum(1 for _ in f)
            except (UnicodeDecodeError, PermissionError):
                # Skip binary files or files we can't read
                return None

            # Create relative path from root
            try:
                relative_path = str(file_path.relative_to(self.root_path))
            except ValueError:
                relative_path = str(file_path)

            return FileInfo(
                path=str(file_path),
                relative_path=relative_path,
                file_type=file_type,
                size_bytes=size_bytes,
                lines=lines
            )

        except Exception as e:
            # Skip files that cause errors
            print(f"Warning: Could not process {file_path}: {e}")
            return None

    def get_statistics(self, files: List[FileInfo]) -> Dict:
        """
        Get statistics about discovered files

        Returns summary like specification example:
            TIME: ~100ms
            RESULT: 6 files identified
        """
        stats = {
            'total_files': len(files),
            'by_type': {},
            'total_lines': sum(f.lines for f in files),
            'total_size_bytes': sum(f.size_bytes for f in files),
        }

        # Count by file type
        for file_info in files:
            file_type = file_info.file_type.value
            if file_type not in stats['by_type']:
                stats['by_type'][file_type] = 0
            stats['by_type'][file_type] += 1

        return stats


# ============================================================================
# STEP 2: AST PARSER (Tree-sitter Integration)
# ============================================================================

@dataclass
class FunctionDefinition:
    """Represents a function definition found in code"""
    name: str
    file_path: str
    line_number: int
    end_line: int
    parameters: List[str]
    is_exported: bool
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class FunctionCall:
    """Represents a function call found in code"""
    function_name: str
    file_path: str
    line_number: int
    calling_function: Optional[str] = None  # What function contains this call
    arguments_count: int = 0


@dataclass
class ImportStatement:
    """Represents an import statement"""
    imported_names: List[str]
    source_module: str
    file_path: str
    line_number: int
    is_default_import: bool = False


@dataclass
class ExportStatement:
    """Represents an export statement"""
    exported_names: List[str]
    file_path: str
    line_number: int
    is_default_export: bool = False


@dataclass
class ParsedFile:
    """Result of parsing a single file"""
    file_path: str
    file_type: FileType
    functions: List[FunctionDefinition]
    calls: List[FunctionCall]
    imports: List[ImportStatement]
    exports: List[ExportStatement]
    parse_errors: List[str] = field(default_factory=list)


class CodeParser:
    """
    Parse code files using Tree-sitter

    Implementation of STEP 2a & 2b from specification:
    - Read file into memory
    - Convert to Abstract Syntax Tree (AST)
    - Walk AST looking for:
      A. Function definitions
      B. Function calls
      C. Imports
      D. Exports
    - Extract all relevant information
    """

    def __init__(self):
        """Initialize Tree-sitter parsers for each language"""
        self.parsers = {}

        # Initialize Python parser
        PY_LANGUAGE = Language(tspython.language())
        py_parser = Parser(PY_LANGUAGE)
        self.parsers[FileType.PYTHON] = py_parser

        # Initialize JavaScript parser
        JS_LANGUAGE = Language(tsjavascript.language())
        js_parser = Parser(JS_LANGUAGE)
        self.parsers[FileType.JAVASCRIPT] = js_parser
        self.parsers[FileType.JSX] = js_parser

        # Initialize TypeScript parser
        TS_LANGUAGE = Language(tstypescript.language_typescript())
        ts_parser = Parser(TS_LANGUAGE)
        self.parsers[FileType.TYPESCRIPT] = ts_parser

        # Initialize TSX parser
        TSX_LANGUAGE = Language(tstypescript.language_tsx())
        tsx_parser = Parser(TSX_LANGUAGE)
        self.parsers[FileType.TSX] = tsx_parser

    def parse_file(self, file_info: FileInfo) -> ParsedFile:
        """
        Parse a single file and extract all code entities

        Implementation of STEP 2a from specification:
        STEP 1: Read entire file into memory
        STEP 2: Convert to Abstract Syntax Tree (AST)
        STEP 3: Walk the AST looking for entities
        STEP 4: Store all extracted information

        Args:
            file_info: Information about the file to parse

        Returns:
            ParsedFile with all extracted entities
        """
        parsed_file = ParsedFile(
            file_path=file_info.path,
            file_type=file_info.file_type,
            functions=[],
            calls=[],
            imports=[],
            exports=[],
            parse_errors=[]
        )

        try:
            # STEP 1: Read entire file into memory
            with open(file_info.path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                source_bytes = source_code.encode('utf-8')

            # STEP 2: Convert to Abstract Syntax Tree (AST)
            parser = self.parsers.get(file_info.file_type)
            if not parser:
                parsed_file.parse_errors.append(f"No parser for {file_info.file_type}")
                return parsed_file

            tree = parser.parse(source_bytes)
            root_node = tree.root_node

            # STEP 3: Walk the AST looking for entities
            if file_info.file_type == FileType.PYTHON:
                self._parse_python(root_node, source_code, parsed_file)
            else:
                self._parse_javascript(root_node, source_code, parsed_file)

        except Exception as e:
            parsed_file.parse_errors.append(f"Parse error: {str(e)}")

        return parsed_file

    def _parse_python(self, root_node: Node, source_code: str, parsed_file: ParsedFile):
        """
        Parse Python-specific syntax

        Looks for:
        - Function definitions: def function_name(...)
        - Function calls: function_name(...)
        - Imports: import X, from X import Y
        """
        self._extract_python_functions(root_node, source_code, parsed_file)
        self._extract_python_calls(root_node, source_code, parsed_file)
        self._extract_python_imports(root_node, source_code, parsed_file)

    def _parse_javascript(self, root_node: Node, source_code: str, parsed_file: ParsedFile):
        """
        Parse JavaScript/TypeScript syntax

        Looks for:
        - Function definitions: function X(...), const X = () => {}
        - Function calls: functionName(...)
        - Imports: import { X } from 'Y'
        - Exports: export { X }, export function X
        """
        self._extract_js_functions(root_node, source_code, parsed_file)
        self._extract_js_calls(root_node, source_code, parsed_file)
        self._extract_js_imports(root_node, source_code, parsed_file)
        self._extract_js_exports(root_node, source_code, parsed_file)

    def _extract_python_functions(self, node: Node, source: str, parsed: ParsedFile):
        """Extract Python function definitions (STEP 3A)"""
        if node.type == 'function_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                func_name = self._get_node_text(name_node, source)

                # Get parameters
                params = []
                params_node = node.child_by_field_name('parameters')
                if params_node:
                    params = self._extract_python_parameters(params_node, source)

                # Check if decorated (exported via decorator or at module level)
                is_exported = self._is_python_exported(node, source)

                # Check if async
                is_async = any(child.type == 'async' for child in node.children)

                # Get decorators
                decorators = self._extract_python_decorators(node, source)

                func_def = FunctionDefinition(
                    name=func_name,
                    file_path=parsed.file_path,
                    line_number=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parameters=params,
                    is_exported=is_exported,
                    is_async=is_async,
                    decorators=decorators
                )
                parsed.functions.append(func_def)

        # Recursively process children
        for child in node.children:
            self._extract_python_functions(child, source, parsed)

    def _extract_python_calls(self, node: Node, source: str, parsed: ParsedFile):
        """Extract Python function calls (STEP 3B)"""
        if node.type == 'call':
            func_node = node.child_by_field_name('function')
            if func_node:
                func_name = self._get_node_text(func_node, source)

                # Find containing function
                containing_func = self._find_containing_function(node, source)

                call = FunctionCall(
                    function_name=func_name,
                    file_path=parsed.file_path,
                    line_number=node.start_point[0] + 1,
                    calling_function=containing_func
                )
                parsed.calls.append(call)

        # Recursively process children
        for child in node.children:
            self._extract_python_calls(child, source, parsed)

    def _extract_python_imports(self, node: Node, source: str, parsed: ParsedFile):
        """Extract Python import statements (STEP 3C)"""
        if node.type == 'import_statement':
            # import module
            imported_names = []
            for child in node.children:
                if child.type == 'dotted_name':
                    imported_names.append(self._get_node_text(child, source))

            if imported_names:
                imp = ImportStatement(
                    imported_names=imported_names,
                    source_module=imported_names[0],
                    file_path=parsed.file_path,
                    line_number=node.start_point[0] + 1
                )
                parsed.imports.append(imp)

        elif node.type == 'import_from_statement':
            # from module import X, Y
            source_module = ""
            imported_names = []

            for child in node.children:
                if child.type == 'dotted_name':
                    source_module = self._get_node_text(child, source)
                elif child.type == 'dotted_name' or child.type == 'identifier':
                    imported_names.append(self._get_node_text(child, source))

            if imported_names:
                imp = ImportStatement(
                    imported_names=imported_names,
                    source_module=source_module,
                    file_path=parsed.file_path,
                    line_number=node.start_point[0] + 1
                )
                parsed.imports.append(imp)

        # Recursively process children
        for child in node.children:
            self._extract_python_imports(child, source, parsed)

    def _extract_js_functions(self, node: Node, source: str, parsed: ParsedFile):
        """Extract JavaScript/TypeScript function definitions (STEP 3A)"""
        # function declaration: function name(...) {}
        if node.type == 'function_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                self._create_js_function(node, name_node, source, parsed)

        # arrow function: const name = () => {}
        elif node.type == 'lexical_declaration' or node.type == 'variable_declaration':
            for child in node.children:
                if child.type == 'variable_declarator':
                    name_node = child.child_by_field_name('name')
                    value_node = child.child_by_field_name('value')
                    if name_node and value_node:
                        if value_node.type in ('arrow_function', 'function'):
                            self._create_js_function(value_node, name_node, source, parsed, node)

        # Recursively process children
        for child in node.children:
            self._extract_js_functions(child, source, parsed)

    def _create_js_function(self, func_node: Node, name_node: Node, source: str,
                           parsed: ParsedFile, parent_node: Node = None):
        """Helper to create JavaScript function definition"""
        func_name = self._get_node_text(name_node, source)

        # Get parameters
        params = []
        params_node = func_node.child_by_field_name('parameters')
        if params_node:
            params = self._extract_js_parameters(params_node, source)

        # Check if exported
        is_exported = self._is_js_exported(func_node, parent_node)

        # Check if async
        is_async = any(child.type == 'async' for child in func_node.children)

        func_def = FunctionDefinition(
            name=func_name,
            file_path=parsed.file_path,
            line_number=func_node.start_point[0] + 1,
            end_line=func_node.end_point[0] + 1,
            parameters=params,
            is_exported=is_exported,
            is_async=is_async
        )
        parsed.functions.append(func_def)

    def _extract_js_calls(self, node: Node, source: str, parsed: ParsedFile):
        """Extract JavaScript function calls (STEP 3B)"""
        if node.type == 'call_expression':
            func_node = node.child_by_field_name('function')
            if func_node:
                func_name = self._get_node_text(func_node, source)

                # Find containing function
                containing_func = self._find_containing_function(node, source)

                call = FunctionCall(
                    function_name=func_name,
                    file_path=parsed.file_path,
                    line_number=node.start_point[0] + 1,
                    calling_function=containing_func
                )
                parsed.calls.append(call)

        # Recursively process children
        for child in node.children:
            self._extract_js_calls(child, source, parsed)

    def _extract_js_imports(self, node: Node, source: str, parsed: ParsedFile):
        """Extract JavaScript/TypeScript imports (STEP 3C)"""
        if node.type == 'import_statement':
            source_module = ""
            imported_names = []
            is_default = False

            # Get source module
            source_node = node.child_by_field_name('source')
            if source_node:
                source_module = self._get_node_text(source_node, source).strip('"\'')

            # Get imported names
            for child in node.children:
                if child.type == 'import_clause':
                    for subchild in child.children:
                        if subchild.type == 'identifier':
                            imported_names.append(self._get_node_text(subchild, source))
                            is_default = True
                        elif subchild.type == 'named_imports':
                            for import_spec in subchild.children:
                                if import_spec.type == 'import_specifier':
                                    name = import_spec.child_by_field_name('name')
                                    if name:
                                        imported_names.append(self._get_node_text(name, source))

            if imported_names:
                imp = ImportStatement(
                    imported_names=imported_names,
                    source_module=source_module,
                    file_path=parsed.file_path,
                    line_number=node.start_point[0] + 1,
                    is_default_import=is_default
                )
                parsed.imports.append(imp)

        # Recursively process children
        for child in node.children:
            self._extract_js_imports(child, source, parsed)

    def _extract_js_exports(self, node: Node, source: str, parsed: ParsedFile):
        """Extract JavaScript/TypeScript exports (STEP 3D)"""
        if node.type == 'export_statement':
            exported_names = []
            is_default = False

            for child in node.children:
                if child.type == 'export_clause':
                    for spec in child.children:
                        if spec.type == 'export_specifier':
                            name = spec.child_by_field_name('name')
                            if name:
                                exported_names.append(self._get_node_text(name, source))
                elif child.type == 'identifier':
                    exported_names.append(self._get_node_text(child, source))
                elif child.type == 'lexical_declaration' or child.type == 'function_declaration':
                    # export const X = ... or export function X
                    name_node = child.child_by_field_name('name')
                    if name_node:
                        exported_names.append(self._get_node_text(name_node, source))

            # Check for default export
            for child in node.children:
                if self._get_node_text(child, source) == 'default':
                    is_default = True
                    break

            if exported_names:
                exp = ExportStatement(
                    exported_names=exported_names,
                    file_path=parsed.file_path,
                    line_number=node.start_point[0] + 1,
                    is_default_export=is_default
                )
                parsed.exports.append(exp)

        # Recursively process children
        for child in node.children:
            self._extract_js_exports(child, source, parsed)

    # Helper methods

    def _get_node_text(self, node: Node, source: str) -> str:
        """Extract text content of a node"""
        return source[node.start_byte:node.end_byte]

    def _extract_python_parameters(self, params_node: Node, source: str) -> List[str]:
        """Extract parameter names from Python function"""
        params = []
        for child in params_node.children:
            if child.type == 'identifier':
                params.append(self._get_node_text(child, source))
        return params

    def _extract_js_parameters(self, params_node: Node, source: str) -> List[str]:
        """Extract parameter names from JavaScript function"""
        params = []
        for child in params_node.children:
            if child.type in ('identifier', 'required_parameter'):
                params.append(self._get_node_text(child, source))
        return params

    def _extract_python_decorators(self, func_node: Node, source: str) -> List[str]:
        """Extract decorators from Python function"""
        decorators = []
        # Look for decorated_definition parent
        parent = func_node.parent
        if parent and parent.type == 'decorated_definition':
            for child in parent.children:
                if child.type == 'decorator':
                    decorators.append(self._get_node_text(child, source))
        return decorators

    def _is_python_exported(self, func_node: Node, source: str) -> bool:
        """Check if Python function is exported (module-level or in __all__)"""
        # In Python, functions at module level are considered "exported"
        # This is a simplified check - could be enhanced
        parent = func_node.parent
        return parent and parent.type == 'module'

    def _is_js_exported(self, func_node: Node, parent_node: Node = None) -> bool:
        """Check if JavaScript function has export keyword"""
        # Check parent nodes for export statement
        check_node = parent_node if parent_node else func_node
        parent = check_node.parent
        while parent:
            if parent.type == 'export_statement':
                return True
            parent = parent.parent
        return False

    def _find_containing_function(self, node: Node, source: str) -> Optional[str]:
        """Find the function that contains this node"""
        parent = node.parent
        while parent:
            if parent.type in ('function_definition', 'function_declaration'):
                name_node = parent.child_by_field_name('name')
                if name_node:
                    return self._get_node_text(name_node, source)
            elif parent.type == 'lexical_declaration':
                # Could be arrow function
                for child in parent.children:
                    if child.type == 'variable_declarator':
                        name_node = child.child_by_field_name('name')
                        if name_node:
                            return self._get_node_text(name_node, source)
            parent = parent.parent
        return None
