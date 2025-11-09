"""
AI Query Agent with Semantic Graph Context
Uses full graph context for intelligent query understanding
"""

from typing import Dict, Optional, List
import json
import os


class SemanticQueryAgent:
    """
    AI Agent that uses semantic graph context for better understanding

    IMPROVEMENTS:
    1. Passes graph context to AI (not just function names)
    2. Handles generic queries ("remove log files", "fix checkout error")
    3. Uses module categorization for better matching
    4. Can trace errors through dependencies
    5. Understands code structure from graph
    """

    def __init__(self, model_type: str = "gemini"):
        """Initialize enhanced AI agent"""
        self.model_type = model_type
        self.enabled = False
        self._setup_llm()

    def _setup_llm(self):
        """Setup LLM with API key"""
        if self.model_type == "gemini":
            try:
                import google.generativeai as genai
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-2.0-flash')
                    self.enabled = True
                else:
                    print("⚠️  GEMINI_API_KEY not set. Using fallback.")
                    self.enabled = False
            except ImportError:
                print("⚠️  google-generativeai not installed.")
                self.enabled = False

    def parse_user_intent(
        self,
        prompt: str,
        orchestrator_or_functions  # Can be orchestrator OR function list (backwards compatible)
    ) -> Dict:
        """
        Parse user intent - backwards compatible method

        Args:
            prompt: User's query
            orchestrator_or_functions: Either SemanticGraphOrchestrator (new) or list of functions (old)
        """
        # Check if it's an orchestrator object or just a list
        if hasattr(orchestrator_or_functions, 'graph'):
            # New way: full orchestrator with graph context
            return self.parse_user_intent_with_context(prompt, orchestrator_or_functions)
        else:
            # Old way: just function names (fallback)
            # Convert to basic dict for compatibility
            return {
                "function_name": None,
                "action": "impact",
                "confidence": 0.3,
                "reasoning": "Need orchestrator object for full context analysis"
            }

    def parse_user_intent_with_context(
        self,
        prompt: str,
        orchestrator  # SemanticGraphOrchestrator with full graph context
    ) -> Dict:
        """
        Parse user intent using FULL semantic graph context

        This is the key improvement - we pass the ENTIRE graph context to AI!

        Args:
            prompt: User's query
            orchestrator: Orchestrator with graph, indexes, modules

        Returns:
            Dict with function_name, action, confidence, reasoning
        """
        if not self.enabled:
            return self._fallback_with_graph_search(prompt, orchestrator)

        # BUILD RICH CONTEXT FROM SEMANTIC GRAPH
        context = self._build_graph_context(orchestrator)

        # Use AI with full context
        return self._parse_with_gemini_enhanced(prompt, context, orchestrator)

    def _build_graph_context(self, orchestrator) -> Dict:
        """
        Build rich context from semantic graph

        This extracts useful information from the graph that helps AI understand:
        - Module structure (checkout, payment, invoices)
        - Function purposes (from names and locations)
        - Criticality levels
        - Common patterns
        - FULL DEPENDENCY GRAPH (nodes + edges)
        """
        graph = orchestrator.graph
        analyzer = orchestrator.analyzer

        # Group functions by module/directory
        modules = {}
        for node_id, node in graph.nodes.items():
            # Extract module from file path
            # e.g., "src/checkout/payment.py" → "checkout"
            parts = node.file_path.split('/')
            if len(parts) > 1:
                module = parts[-2]  # Directory name
            else:
                module = "root"

            if module not in modules:
                modules[module] = []

            # Store function with useful info
            modules[module].append({
                'name': node.name,
                'file': node.file_path,
                'usages': len(analyzer.indexes.function_called_by.get(node_id, [])),
                'calls': len(analyzer.indexes.function_calls.get(node_id, []))
            })

        # Find high-usage functions (likely important)
        important_functions = []
        for node_id, node in list(graph.nodes.items())[:20]:
            usage_count = len(analyzer.indexes.function_called_by.get(node_id, []))
            if usage_count > 3:  # Used more than 3 times
                important_functions.append({
                    'name': node.name,
                    'usages': usage_count,
                    'module': self._extract_module(node.file_path)
                })

        # Get full graph structure (nodes + edges) for AI to analyze
        graph_dict = graph.to_dict()

        # Create simplified dependency map for better token efficiency
        # Format: "function_name -> [list of functions it calls]"
        dependency_map = {}
        for edge in graph_dict['edges']:
            caller = edge['source_id']  # Fixed: was 'from_node'
            callee = edge['target_id']  # Fixed: was 'to_node'
            if caller not in dependency_map:
                dependency_map[caller] = []
            dependency_map[caller].append(callee)

        # Generate DOT format for AI to visualize structure
        dot_graph = graph.to_dot(max_nodes=50)  # Limit to 50 nodes for token efficiency

        return {
            'modules': modules,
            'important_functions': important_functions,
            'total_functions': len(graph.nodes),
            'total_files': len(set(n.file_path for n in graph.nodes.values())),
            'dependency_map': dependency_map,  # Full dependency relationships
            'dot_graph': dot_graph,  # NEW: Graph in DOT format for visualization
            'graph_summary': {
                'total_nodes': len(graph_dict['nodes']),
                'total_edges': len(graph_dict['edges']),
                'statistics': graph_dict['statistics']
            }
        }

    def _extract_module(self, file_path: str) -> str:
        """Extract module name from file path"""
        parts = file_path.split('/')
        if len(parts) > 1:
            return parts[-2]
        return "root"

    def _parse_with_gemini_enhanced(
        self,
        prompt: str,
        context: Dict,
        orchestrator
    ) -> Dict:
        """
        Use Gemini with FULL graph context

        This is much smarter than just passing function names!
        """

        # Create rich prompt with graph context
        system_prompt = f"""You are an intelligent code analysis assistant with access to a semantic dependency graph.

=== CODEBASE STRUCTURE ===
Total Functions: {context['total_functions']}
Total Files: {context['total_files']}
Total Graph Nodes: {context['graph_summary']['total_nodes']}
Total Dependencies: {context['graph_summary']['total_edges']}

=== MODULES IN CODEBASE ===
{json.dumps(context['modules'], indent=2)}

=== IMPORTANT/FREQUENTLY USED FUNCTIONS ===
{json.dumps(context['important_functions'], indent=2)}

=== DEPENDENCY GRAPH (function → calls) ===
{json.dumps(list(context['dependency_map'].items())[:50], indent=2)}
Note: Showing first 50 dependencies. Full graph available.

=== GRAPH VISUALIZATION (DOT FORMAT) ===
{context.get('dot_graph', 'Not available')}
Note: This shows the dependency graph structure visually.
Use this to understand relationships between functions.

=== USER QUERY ===
"{prompt}"

=== YOUR TASK ===
Analyze the user's query and determine:

1. **What function(s) are they asking about?**
   - If they mention a specific function name, use that
   - If they use generic terms like "log files", "checkout", "payment", map to functions in that module
   - If they mention an error, try to identify which module/function might cause it
   - Be flexible with partial matches (e.g., "payment" could be "processPayment", "handlePayment", etc.)

2. **What action do they want?**
   - Options: "rename", "delete", "update", "refactor", "usages", "impact", "safety_check", "error_trace", "find_by_purpose"
   - "remove/delete log files" → action: "find_by_purpose", look for functions with "log" in name or in "logging" module
   - "error in checkout" → action: "error_trace", find functions in checkout module
   - "is it safe to..." → action: "safety_check"

3. **Confidence (0-1)**
   - High (0.8-1.0) if specific function mentioned
   - Medium (0.5-0.7) if module mentioned but need to find function
   - Low (0.3-0.4) if very generic query

4. **Reasoning**
   - Explain how you mapped the query to the codebase

=== SPECIAL CASES ===
- Generic queries: Return action="find_by_purpose" with search terms
- Error queries: Return action="error_trace" with module name
- Multiple functions: Pick the most relevant one or return "multiple"

Respond ONLY with valid JSON:
{{
    "function_name": "exact_function_name_or_module_name_or_search_term",
    "action": "one_of_the_actions",
    "confidence": 0.95,
    "reasoning": "explanation",
    "search_terms": ["optional", "keywords", "for", "generic", "queries"],
    "module": "optional_module_name"
}}"""

        try:
            response = self.model.generate_content(system_prompt)
            result_text = response.text.strip()

            # Parse JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # If generic query, search graph for matching functions
            if result.get("action") == "find_by_purpose":
                matching_functions = self._find_functions_by_purpose(
                    result.get("search_terms", []),
                    result.get("module"),
                    orchestrator
                )
                result["matching_functions"] = matching_functions
                if matching_functions:
                    result["function_name"] = matching_functions[0]  # Pick best match

            return result

        except Exception as e:
            print(f"⚠️  Enhanced Gemini parsing failed: {e}")
            return self._fallback_with_graph_search(prompt, orchestrator)

    def _find_functions_by_purpose(
        self,
        search_terms: List[str],
        module_filter: Optional[str],
        orchestrator
    ) -> List[str]:
        """
        Search graph for functions matching purpose/keywords

        This uses the semantic graph to find relevant functions!
        """
        graph = orchestrator.graph
        matching = []

        for node_id, node in graph.nodes.items():
            # Check if any search term in function name
            name_lower = node.name.lower()
            file_lower = node.file_path.lower()

            matches = False
            for term in search_terms:
                term_lower = term.lower()
                if term_lower in name_lower or term_lower in file_lower:
                    matches = True
                    break

            # Filter by module if specified
            if module_filter:
                if module_filter.lower() not in file_lower:
                    matches = False

            if matches:
                matching.append(node.name)

        return matching[:10]  # Return top 10 matches

    def _fallback_with_graph_search(self, prompt: str, orchestrator) -> Dict:
        """
        Fallback that still uses graph to search

        Even without AI, we can search the graph intelligently!
        """
        prompt_lower = prompt.lower()
        graph = orchestrator.graph

        # Extract keywords from prompt
        keywords = []
        for word in prompt_lower.split():
            if len(word) > 3 and word.isalnum():
                keywords.append(word)

        # Search graph for matching functions
        matches = []
        for node_id, node in graph.nodes.items():
            name_lower = node.name.lower()
            for keyword in keywords:
                if keyword in name_lower:
                    matches.append(node.name)
                    break

        # Determine action
        action = "impact"
        if any(w in prompt_lower for w in ["remove", "delete"]):
            action = "delete"
        elif any(w in prompt_lower for w in ["safe", "safety"]):
            action = "safety_check"
        elif any(w in prompt_lower for w in ["error", "fix", "debug"]):
            action = "error_trace"
        elif any(w in prompt_lower for w in ["find", "where", "usage"]):
            action = "usages"

        return {
            "function_name": matches[0] if matches else None,
            "action": action,
            "confidence": 0.4,
            "reasoning": f"Pattern matching with graph search. Found {len(matches)} potential matches.",
            "matching_functions": matches[:5]
        }
