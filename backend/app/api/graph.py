"""
Semantic Graph API Routes
POST /graph/analyze - Analyze repository
GET /graph/dependencies - Get dependency graph
POST /graph/search - Semantic code search
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from pathlib import Path

from ..services.semantic_graph import SemanticGraphOrchestrator

router = APIRouter(prefix="/graph", tags=["Semantic Graph"])

# Global orchestrator cache (in production, use Redis or DB)
_orchestrators: Dict[str, SemanticGraphOrchestrator] = {}


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request to analyze a repository"""
    repo_path: str
    force_rebuild: bool = False


class AnalyzeResponse(BaseModel):
    """Response from repository analysis"""
    status: str
    message: str
    statistics: Dict
    graph_id: str


class FunctionUsageResponse(BaseModel):
    """Response with function usage details"""
    function_name: str
    total_usages: int
    files_affected: int
    breakdown: Dict
    summary: Dict


class ImpactAssessmentRequest(BaseModel):
    """Request for impact assessment"""
    repo_path: str
    function_name: str
    change_description: str = "Refactor"


class ImpactAssessmentResponse(BaseModel):
    """Response with complete impact assessment"""
    function_name: str
    change_description: str
    summary: Dict
    risk_score: Dict
    modules: List[Dict]
    business_impact: Dict


class GraphVisualizationResponse(BaseModel):
    """Response with graph data for visualization"""
    nodes: List[Dict]
    edges: List[Dict]
    metadata: Dict


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repository(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Analyze a repository and build semantic graph

    STEP 1-4 from specification:
    - Discover files
    - Parse with Tree-sitter
    - Build graph
    - Create indexes

    Returns:
        Complete graph statistics
    """
    try:
        repo_path = request.repo_path

        # Check if user provided a GitHub URL (not supported yet)
        if repo_path.startswith(("https://", "http://", "github.com", "git@")):
            raise HTTPException(
                status_code=400,
                detail=f"GitHub URLs are not supported. Please clone the repository first and provide the local path. "
                       f"Example: git clone {repo_path} && provide the local folder path."
            )

        # Validate path exists
        if not os.path.exists(repo_path):
            raise HTTPException(
                status_code=404,
                detail=f"Local repository path not found: {repo_path}. "
                       f"Please provide an existing folder path on your computer."
            )

        # Check if already analyzed
        if repo_path in _orchestrators and not request.force_rebuild:
            orchestrator = _orchestrators[repo_path]
            stats = orchestrator.get_statistics()
            return AnalyzeResponse(
                status="cached",
                message="Using cached graph",
                statistics=stats,
                graph_id=repo_path
            )

        # Build graph
        orchestrator = SemanticGraphOrchestrator(repo_path)
        orchestrator.build_graph()

        # Cache it
        _orchestrators[repo_path] = orchestrator

        # Debug logging
        print(f"\n✅ Repository analyzed and cached:")
        print(f"   Path: {repo_path}")
        print(f"   Cache now contains: {list(_orchestrators.keys())}")

        # Get statistics
        stats = orchestrator.get_statistics()

        return AnalyzeResponse(
            status="success",
            message=f"Analyzed repository: {stats['files_discovered']} files, {stats['functions_found']} functions",
            statistics=stats,
            graph_id=repo_path
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/function/{function_name}/usages", response_model=FunctionUsageResponse)
async def get_function_usages(function_name: str, repo_path: str):
    """
    Get all usages of a function

    STEP 5, 7 from specification:
    - Query graph for ALL usages
    - Return: definition, exports, imports, calls, tests

    Returns:
        Complete usage report with 47 locations (example)
    """
    try:
        # Get orchestrator
        if repo_path not in _orchestrators:
            raise HTTPException(
                status_code=404,
                detail=f"Repository not analyzed. Call /graph/analyze first."
            )

        orchestrator = _orchestrators[repo_path]

        # Find usages
        usage_report = orchestrator.find_usages(function_name)

        if not usage_report:
            raise HTTPException(status_code=404, detail=f"Function not found: {function_name}")

        return FunctionUsageResponse(
            function_name=usage_report.function_name,
            total_usages=usage_report.total_usages,
            files_affected=len(usage_report.files_affected),
            breakdown=usage_report.to_dict()['breakdown'],
            summary=usage_report.to_dict()['summary']
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/assess-impact", response_model=ImpactAssessmentResponse)
async def assess_change_impact(request: ImpactAssessmentRequest):
    """
    Assess complete impact of changing a function

    STEP 6-9 from specification:
    - Categorize by module
    - Assign criticality levels
    - Calculate risk score
    - Assess business impact

    Returns:
        Complete impact assessment with risk level and revenue impact
    """
    try:
        repo_path = request.repo_path

        # Get orchestrator
        if repo_path not in _orchestrators:
            raise HTTPException(
                status_code=404,
                detail=f"Repository not analyzed. Call /graph/analyze first."
            )

        orchestrator = _orchestrators[repo_path]

        # Assess impact
        impact_report = orchestrator.assess_change_impact(
            request.function_name,
            request.change_description
        )

        if not impact_report:
            raise HTTPException(
                status_code=404,
                detail=f"Function not found: {request.function_name}"
            )

        impact_dict = impact_report.to_dict()

        return ImpactAssessmentResponse(
            function_name=impact_dict['function_name'],
            change_description=impact_dict['change_description'],
            summary=impact_dict['summary'],
            risk_score=impact_dict['risk_score'],
            modules=impact_dict['modules'],
            business_impact=impact_dict['business_impact']
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impact assessment failed: {str(e)}")


@router.get("/visualization", response_model=GraphVisualizationResponse)
async def get_graph_visualization(repo_path: str, function_name: Optional[str] = None):
    """
    Get graph data formatted for visualization

    Returns nodes and edges for React Flow or D3.js visualization

    Format matches PART B-G from specification:
    - Nodes with position, type, criticality
    - Edges with source, target, type
    - Metadata for rendering
    """
    try:
        # Get orchestrator
        if repo_path not in _orchestrators:
            raise HTTPException(
                status_code=404,
                detail=f"Repository not analyzed. Call /graph/analyze first."
            )

        orchestrator = _orchestrators[repo_path]
        graph = orchestrator.graph

        # Convert to visualization format
        nodes = []
        edges = []

        # If function specified, show its subgraph
        if function_name:
            usage_report = orchestrator.find_usages(function_name)
            if not usage_report:
                raise HTTPException(status_code=404, detail=f"Function not found: {function_name}")

            # Create node for target function
            target_node = orchestrator.analyzer.get_function_details(function_name)
            if target_node:
                nodes.append({
                    'id': target_node.id,
                    'label': target_node.name,
                    'type': 'target',
                    'file': target_node.file_path,
                    'line': target_node.line_number,
                    'usages': usage_report.total_usages,
                    'exported': target_node.is_exported
                })

            # Add caller nodes
            callers = orchestrator.analyzer.get_callers(function_name)
            for caller_id in callers[:20]:  # Limit to 20 for visualization
                caller_node = graph.get_node(caller_id)
                if caller_node:
                    nodes.append({
                        'id': caller_node.id,
                        'label': caller_node.name,
                        'type': 'caller',
                        'file': caller_node.file_path,
                        'line': caller_node.line_number
                    })

                    # Add edge
                    edges.append({
                        'id': f"{caller_id}-calls-{target_node.id}",
                        'source': caller_id,
                        'target': target_node.id,
                        'type': 'calls'
                    })

        else:
            # Show full graph (limited)
            for node_id, node in list(graph.nodes.items())[:50]:  # Limit to 50 nodes
                nodes.append({
                    'id': node.id,
                    'label': node.name,
                    'type': node.type.value,
                    'file': node.file_path,
                    'line': node.line_number,
                    'exported': node.is_exported if hasattr(node, 'is_exported') else False
                })

            # Add edges
            for edge in graph.edges[:100]:  # Limit to 100 edges
                edges.append({
                    'id': edge.id,
                    'source': edge.source_id,
                    'target': edge.target_id,
                    'type': edge.edge_type.value
                })

        return GraphVisualizationResponse(
            nodes=nodes,
            edges=edges,
            metadata={
                'total_nodes': len(graph.nodes),
                'total_edges': len(graph.edges),
                'displayed_nodes': len(nodes),
                'displayed_edges': len(edges),
                'focused_function': function_name
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization failed: {str(e)}")


@router.get("/stats")
async def get_statistics(repo_path: str):
    """Get graph statistics"""
    if repo_path not in _orchestrators:
        raise HTTPException(
            status_code=404,
            detail=f"Repository not analyzed. Call /graph/analyze first."
        )

    orchestrator = _orchestrators[repo_path]
    return orchestrator.get_statistics()


@router.get("/export/dot")
async def export_graph_dot(
    repo_path: str,
    max_nodes: int = 100,
    focus_function: Optional[str] = None
):
    """
    Export graph in DOT format for visualization

    DOT format can be:
    - Visualized with Graphviz tools
    - Passed to AI models for better understanding
    - Used by frontend visualization libraries

    Args:
        repo_path: Path to analyzed repository
        max_nodes: Maximum nodes to include (default 100)
        focus_function: Optional function to focus on with its dependencies

    Returns:
        Plain text DOT format string
    """
    if repo_path not in _orchestrators:
        raise HTTPException(
            status_code=404,
            detail=f"Repository not analyzed. Call /graph/analyze first."
        )

    orchestrator = _orchestrators[repo_path]
    dot_string = orchestrator.graph.to_dot(max_nodes=max_nodes, focus_function=focus_function)

    return {
        "format": "dot",
        "content": dot_string,
        "metadata": {
            "max_nodes": max_nodes,
            "focus_function": focus_function,
            "total_nodes": len(orchestrator.graph.nodes),
            "total_edges": len(orchestrator.graph.edges)
        }
    }


# ============================================================================
# NATURAL LANGUAGE QUERY ENDPOINT (WITH AI AGENT)
# ============================================================================

class NaturalLanguageQueryRequest(BaseModel):
    """Request for natural language query"""
    repo_path: str
    prompt: str
    use_ai: bool = True  # Use AI agent for semantic understanding


class NaturalLanguageQueryResponse(BaseModel):
    """Response with parsed query and results"""
    understood_intent: str
    extracted_function: str
    extracted_action: str
    confidence: float
    ai_reasoning: str
    analysis_result: Dict


# Initialize AI agent (lazy loading)
_ai_agent = None

def get_ai_agent():
    """Get or create AI agent instance"""
    global _ai_agent
    if _ai_agent is None:
        from ..services.ai_query_agent import SemanticQueryAgent
        _ai_agent = SemanticQueryAgent(model_type="gemini")  # or "gpt"
    return _ai_agent


def parse_natural_language_prompt_legacy(prompt: str, orchestrator: SemanticGraphOrchestrator) -> tuple:
    """
    Parse natural language prompt to extract intent

    This is a SIMPLE pattern-matching approach (no LLM needed!)
    For hackathon demo, this works great.

    Examples:
    - "I want to rename calculatePrice" → ("calculatePrice", "rename")
    - "Show impact of changing checkout" → ("checkout", "impact")
    - "What breaks if I update processPayment?" → ("processPayment", "impact")
    """
    prompt_lower = prompt.lower()

    # Extract action intent
    action = "impact"  # default
    if any(word in prompt_lower for word in ["rename", "renaming"]):
        action = "rename"
    elif any(word in prompt_lower for word in ["delete", "remove", "removing"]):
        action = "delete"
    elif any(word in prompt_lower for word in ["update", "change", "modify", "refactor"]):
        action = "update"
    elif any(word in prompt_lower for word in ["usage", "usages", "where", "find"]):
        action = "usages"

    # Try to extract function name
    # Method 1: Look for camelCase or snake_case identifiers
    import re

    # Get all function names from the graph
    all_functions = list(orchestrator.graph.nodes.keys())
    function_names = [name.split(':')[-1] for name in all_functions]

    # Find which function is mentioned in the prompt
    function_name = None
    for func in function_names:
        if func.lower() in prompt_lower:
            function_name = func
            break

    # If no exact match, try partial match
    if not function_name:
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', prompt)
        for word in words:
            for func in function_names:
                if word.lower() in func.lower() and len(word) > 3:
                    function_name = func
                    break
            if function_name:
                break

    return function_name, action


@router.post("/query", response_model=NaturalLanguageQueryResponse)
async def natural_language_query(request: NaturalLanguageQueryRequest):
    """
    Natural language query interface with AI semantic understanding

    NEW: Uses AI agent (Gemini/GPT) to understand user intent semantically!
    - No more if-else keyword matching
    - Real semantic understanding of user queries
    - Handles complex questions like "Is it safe to..."

    Accepts plain English prompts like:
    - "Is it safe to delete the old payment processor?"
    - "I'm thinking of refactoring calculatePrice"
    - "What would break if I rename checkout?"
    - "Show me everywhere processPayment is called"

    If use_ai=False, falls back to pattern matching.

    Example:
        POST /graph/query
        {
            "repo_path": "C:\\Users\\sailo\\MyProject",
            "prompt": "Is it safe to remove the legacy validator?",
            "use_ai": true
        }
    """
    try:
        repo_path = request.repo_path

        # Debug logging
        print(f"\n🔍 Query request received:")
        print(f"   Repo path: {repo_path}")
        print(f"   Prompt: {request.prompt}")
        print(f"   Available orchestrators: {list(_orchestrators.keys())}")

        # Get orchestrator
        if repo_path not in _orchestrators:
            raise HTTPException(
                status_code=404,
                detail=f"Repository not analyzed. Call /graph/analyze first with repo_path: {repo_path}. Available: {list(_orchestrators.keys())}"
            )

        orchestrator = _orchestrators[repo_path]

        # Use AI agent for semantic understanding with FULL graph context
        if request.use_ai:
            ai_agent = get_ai_agent()
            # Pass orchestrator (not just function names!) for rich context
            intent = ai_agent.parse_user_intent(request.prompt, orchestrator)

            function_name = intent["function_name"]
            action = intent["action"]
            confidence = intent["confidence"]
            reasoning = intent["reasoning"]
        else:
            # Fallback to pattern matching
            function_name, action = parse_natural_language_prompt_legacy(request.prompt, orchestrator)
            confidence = 0.6
            reasoning = "Using pattern matching (AI disabled)"

        # Handle generic queries that don't target a specific function
        if not function_name or action == "find_by_purpose":
            # For generic queries, return a summary of the codebase
            return NaturalLanguageQueryResponse(
                understood_intent=request.prompt,
                extracted_function="N/A - Generic Query",
                extracted_action=action or "general_analysis",
                confidence=confidence,
                ai_reasoning=reasoning + " | Generic codebase analysis - no specific function targeted.",
                analysis_result={
                    "function_name": "General Analysis",
                    "summary": {
                        "total_usages": 0,
                        "total_files": len(set(n.file_path for n in orchestrator.graph.nodes.values())),
                        "risk_level": "N/A",
                        "risk_score": 0
                    },
                    "risk_score": {
                        "risk_level": "N/A",
                        "risk_score": 0
                    },
                    "modules": [],
                    "business_impact": {
                        "revenue_impact_range": "N/A",
                        "affected_users": "N/A",
                        "estimated_recovery_time": "N/A"
                    },
                    "safety_recommendation": f"For specific analysis, please query about a particular function. Try: 'What happens if I change [function_name]?'"
                }
            )

        # Execute the appropriate analysis
        result = {}

        if action == "usages":
            usage_report = orchestrator.find_usages(function_name)
            if usage_report:
                result = usage_report.to_dict()
            else:
                raise HTTPException(404, f"Function '{function_name}' not found in codebase")

        elif action == "safety_check":
            # Special handling for safety questions
            impact_report = orchestrator.assess_change_impact(
                function_name,
                change_description="Safety check for modification"
            )
            if impact_report:
                result = impact_report.to_dict()
                # Add safety recommendation
                risk_level = result["risk_score"]["risk_level"]
                if risk_level == "CRITICAL":
                    result["safety_recommendation"] = "⛔ HIGH RISK: Not safe to modify without extensive testing"
                elif risk_level == "HIGH":
                    result["safety_recommendation"] = "⚠️  CAUTION: Requires careful review and testing"
                elif risk_level == "MEDIUM":
                    result["safety_recommendation"] = "✓ MODERATE: Safe with proper testing"
                else:
                    result["safety_recommendation"] = "✓ LOW RISK: Relatively safe to modify"
            else:
                raise HTTPException(404, f"Function '{function_name}' not found in codebase")

        else:  # impact, rename, update, delete, refactor
            impact_report = orchestrator.assess_change_impact(
                function_name,
                change_description=f"{action} function"
            )
            if impact_report:
                result = impact_report.to_dict()
            else:
                raise HTTPException(404, f"Function '{function_name}' not found in codebase")

        return NaturalLanguageQueryResponse(
            understood_intent=f"Analyze {action} impact for '{function_name}'",
            extracted_function=function_name,
            extracted_action=action,
            confidence=confidence,
            ai_reasoning=reasoning,
            analysis_result=result
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"\n❌ ERROR in query endpoint:\n{error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )
