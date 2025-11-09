"""
Example: How to use the Semantic Graph System

This demonstrates the complete pipeline from STEPS 1-9
"""

from backend.app.services.semantic_graph import (
    SemanticGraphOrchestrator,
    analyze_repository,
    analyze_function_change
)


def example_1_basic_usage():
    """
    Example 1: Basic usage - Build graph and analyze a function
    """
    print("=" * 80)
    print("EXAMPLE 1: Basic Graph Building and Analysis")
    print("=" * 80)

    # Initialize orchestrator with repository path
    repo_path = "./my-project"
    orchestrator = SemanticGraphOrchestrator(repo_path)

    # Build the complete semantic graph (STEPS 1-4)
    # This will:
    # - Discover all code files
    # - Parse with Tree-sitter
    # - Build dependency graph
    # - Create indexes
    graph = orchestrator.build_graph(storage_path="./output/code_graph.json")

    # Query for function usages (STEP 5, 7)
    usage_report = orchestrator.find_usages("calculatePrice")
    print(f"\n📍 Found {usage_report.total_usages} usages of 'calculatePrice'")
    print(f"   Across {len(usage_report.files_affected)} files")

    # Assess change impact (STEPS 6-9)
    impact = orchestrator.assess_change_impact(
        "calculatePrice",
        "Rename to computeTotal"
    )

    print(f"\n⚠️  Risk Assessment:")
    print(f"   Risk Level: {impact.risk_score.risk_level.value.upper()}")
    print(f"   Risk Score: {impact.risk_score.total_score} points")
    print(f"   Revenue Impact: {impact.revenue_impact_low} - {impact.revenue_impact_high}")


def example_2_complete_analysis():
    """
    Example 2: Get complete analysis report
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Complete Analysis Report")
    print("=" * 80)

    repo_path = "./my-project"
    orchestrator = SemanticGraphOrchestrator(repo_path)
    orchestrator.build_graph()

    # Get complete analysis (all steps combined)
    analysis = orchestrator.get_complete_analysis(
        function_name="calculatePrice",
        change_description="Rename to computeTotal"
    )

    # Access different parts of the analysis
    print("\n📊 Usage Breakdown:")
    usage = analysis['usage_report']
    print(f"   • Definition: {usage['summary']['definition_count']}")
    print(f"   • Exports: {usage['summary']['export_count']}")
    print(f"   • Imports: {usage['summary']['import_count']}")
    print(f"   • Calls: {usage['summary']['call_count']}")
    print(f"   • Tests: {usage['summary']['test_count']}")

    print("\n⚠️  Impact Assessment:")
    impact = analysis['impact_assessment']
    print(f"   • Total Usages: {impact['summary']['total_usages']}")
    print(f"   • Files Affected: {impact['summary']['total_files']}")
    print(f"   • Risk Level: {impact['summary']['risk_level']}")
    print(f"   • Risk Score: {impact['summary']['risk_score']} points")

    print("\n🎯 Failure Mode Analysis:")
    risk = analysis['risk_analysis']
    print(f"   • Success Rate: {risk['overall_success_rate']}")
    print(f"   • Failure Modes: {risk['summary']['total_failure_modes']}")

    # Export to file
    orchestrator.export_analysis("calculatePrice", "./output/analysis_report.json")


def example_3_quick_functions():
    """
    Example 3: Using quick helper functions
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Quick Analysis Functions")
    print("=" * 80)

    # Quick repository analysis
    orchestrator = analyze_repository(
        repo_path="./my-project",
        output_dir="./output"
    )

    # Quick function change analysis
    analysis = analyze_function_change(
        repo_path="./my-project",
        function_name="calculatePrice",
        change_description="Rename to computeTotal",
        output_path="./output/quick_report.json"
    )

    print(f"\n✅ Analysis complete!")
    print(f"   Report saved to: ./output/quick_report.json")


def example_4_detailed_queries():
    """
    Example 4: Detailed queries and custom analysis
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Detailed Queries")
    print("=" * 80)

    repo_path = "./my-project"
    orchestrator = SemanticGraphOrchestrator(repo_path)
    orchestrator.build_graph()

    function_name = "calculatePrice"

    # 1. Find all usages
    usage_report = orchestrator.find_usages(function_name)

    print(f"\n📍 All Usages of '{function_name}':")
    print(f"\n   Definition:")
    if usage_report.definition:
        loc = usage_report.definition
        print(f"   • {loc.file_path}:{loc.line_number}")
        print(f"     {loc.context}")

    print(f"\n   Imports ({len(usage_report.imports)}):")
    for imp in usage_report.imports[:3]:  # Show first 3
        print(f"   • {imp.file_path}:{imp.line_number}")
        print(f"     {imp.context}")

    print(f"\n   Calls ({len(usage_report.calls)}):")
    for call in usage_report.calls[:5]:  # Show first 5
        containing = call.containing_function or "module-level"
        print(f"   • {call.file_path}:{call.line_number} (in {containing})")
        print(f"     {call.context}")

    # 2. Get risk calculation
    risk_assessment = orchestrator.calculate_risk(function_name, "rename")

    print(f"\n🎯 Failure Mode Analysis:")
    for fm in risk_assessment.failure_modes:
        print(f"\n   {fm.name}:")
        print(f"   • Probability: {fm.probability_label} ({fm.probability_percent}%)")
        print(f"   • Impact: {fm.impact_description}")
        print(f"   • Symptom: {fm.symptom}")
        print(f"   • Recovery: {fm.recovery_time_minutes} minutes")

    print(f"\n   Mitigations:")
    for mitigation in risk_assessment.mitigations:
        print(f"   • {mitigation.strategy} ({mitigation.effectiveness_percent}% effective)")


def example_5_module_breakdown():
    """
    Example 5: Module-by-module breakdown
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Module Breakdown")
    print("=" * 80)

    repo_path = "./my-project"
    orchestrator = SemanticGraphOrchestrator(repo_path)
    orchestrator.build_graph()

    impact = orchestrator.assess_change_impact("calculatePrice")

    print(f"\n📦 Modules Affected ({len(impact.modules)}):\n")

    for module in impact.modules:
        print(f"   {module.module_name} ({module.file_path})")
        print(f"   ├─ Criticality: {module.criticality.value.upper()}")
        print(f"   ├─ Usages: {module.total_usages()}")
        print(f"   │  ├─ Definitions: {module.definition_count}")
        print(f"   │  ├─ Exports: {module.export_count}")
        print(f"   │  ├─ Imports: {module.import_count}")
        print(f"   │  └─ Calls: {module.call_count}")
        print(f"   ├─ Risk: {module.risk_description}")
        print(f"   └─ Impact: {module.impact_description}")
        print()


def example_specification_demo():
    """
    Example that matches the specification exactly

    From user specification:
    "Rename calculatePrice to computeTotal"
    Shows all 47 usages across different modules
    """
    print("\n" + "=" * 80)
    print("SPECIFICATION DEMO: Rename calculatePrice → computeTotal")
    print("=" * 80)

    # This matches the exact specification example
    repo_path = "./my-project"
    orchestrator = SemanticGraphOrchestrator(repo_path)

    print("\n🔍 STEP 1-4: Building Semantic Graph...")
    orchestrator.build_graph()

    print("\n🔍 STEP 7: Query Graph for All Usages")
    print("QUERY: 'Show me EVERYWHERE calculatePrice is used'")

    usage_report = orchestrator.find_usages("calculatePrice")

    if usage_report:
        print(f"\n✓ RESULT: {usage_report.total_usages} LOCATIONS RETURNED")

        print("\n📊 Location Breakdown:")
        print(f"\nDEFINITION & EXPORT:")
        if usage_report.definition:
            print(f"├─ {usage_report.definition.file_path}:{usage_report.definition.line_number}")
            print(f"│  └─ Code: {usage_report.definition.context[:60]}...")

        print(f"\nIMPORTS (need to update): {len(usage_report.imports)}")
        for imp in usage_report.imports:
            print(f"├─ {imp.file_path}:{imp.line_number}")
            print(f"│  └─ Code: {imp.context[:60]}...")

        print(f"\nFUNCTION CALLS (need to update): {len(usage_report.calls)}")
        for call in usage_report.calls[:10]:  # Show first 10
            containing = call.containing_function or "module-level"
            print(f"├─ {call.file_path}:{call.line_number} - in {containing}()")
            print(f"│  └─ Code: {call.context[:60]}...")

    print("\n🔍 STEP 8: Categorize by Module & Criticality")
    impact = orchestrator.assess_change_impact("calculatePrice", "Rename to computeTotal")

    if impact:
        print(f"\nORGANIZE BY MODULE:")
        for module in impact.modules:
            print(f"\n{module.module_name}:")
            print(f"├─ Usages: {module.total_usages()} locations")
            print(f"├─ Risk: {module.risk_description}")
            print(f"└─ Criticality: {module.criticality.value.upper()}")

        print("\n🔍 STEP 9: Calculate Risk Score & Business Impact")
        risk = impact.risk_score
        print(f"\nRISK CALCULATION:")
        print(f"Formula: (Critical×10) + (Secondary×5) + (Tertiary×2) + (Non-Critical×1)")
        print(f"\nCalculation:")
        print(f"├─ Critical Path: {risk.critical_path_usages} usages × 10 = {risk.critical_points} points")
        print(f"├─ Secondary: {risk.secondary_usages} usages × 5 = {risk.secondary_points} points")
        print(f"├─ Tertiary: {risk.tertiary_usages} usages × 2 = {risk.tertiary_points} points")
        print(f"└─ Non-Critical: {risk.non_critical_usages} usages × 1 = {risk.non_critical_points} points")
        print(f"\nRISK_SCORE = {risk.total_score} points")
        print(f"RISK LEVEL: {risk.risk_level.value.upper()}")

        print(f"\nBUSINESS IMPACT:")
        print(f"├─ Revenue Impact: {impact.revenue_impact_low} - {impact.revenue_impact_high} per hour")
        print(f"├─ Affected Users: {impact.affected_users}")
        print(f"└─ Recovery Time: {impact.recovery_time}")

    print("\n🔍 STEP 9c: Failure Mode Analysis")
    risk_assessment = orchestrator.calculate_risk("calculatePrice", "rename")

    print(f"\nWhat could go wrong?")
    for i, fm in enumerate(risk_assessment.failure_modes, 1):
        print(f"\nFAILURE MODE {i}: {fm.name}")
        print(f"├─ Probability: {fm.probability_label} ({fm.probability_percent}%)")
        print(f"│  (with Copilot: {fm.probability_without_graph}%)")
        print(f"├─ Impact: {fm.impact_description}")
        print(f"├─ Symptom: {fm.symptom}")
        print(f"├─ Detection: {fm.detection_method.value}")
        print(f"└─ Recovery: {fm.recovery_time_minutes} min")

    print(f"\nMITIGATION:")
    for mitigation in risk_assessment.mitigations:
        print(f"├─ {mitigation.strategy}")
    print(f"└─ Combined: {risk_assessment.success_rate_percent}% success rate")


if __name__ == "__main__":
    # Run the specification demo
    example_specification_demo()

    # Or run individual examples:
    # example_1_basic_usage()
    # example_2_complete_analysis()
    # example_3_quick_functions()
    # example_4_detailed_queries()
    # example_5_module_breakdown()
