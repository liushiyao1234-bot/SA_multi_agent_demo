"""Compact terminal summaries for workflow results."""

import json

from config import DEBUG


def print_state_summary(state):
    print("\n=== Workflow State ===")

    print(
        f"Customer State:      v{state['versions']['customer_state']}"
    )

    print(
        f"Product Matches:     v{state['versions']['product_matches']} "
        f"{'[STALE]' if state['stale']['product_matches'] else '[CURRENT]'}"
    )

    product_dep = state["dependencies"]["product_matches"]["customer_state_version"]
    print(
        f"  based on Customer State v{product_dep}"
    )

    print(
        f"Candidate Solutions: v{state['versions']['candidate_solutions']} "
        f"{'[STALE]' if state['stale']['candidate_solutions'] else '[CURRENT]'}"
    )

    solution_customer_dep = (
        state["dependencies"]["candidate_solutions"]["customer_state_version"]
    )
    solution_product_dep = (
        state["dependencies"]["candidate_solutions"]["product_matches_version"]
    )

    print(
        f"  based on Customer State v{solution_customer_dep}"
    )
    print(
        f"  based on Product Matches v{solution_product_dep}"
    )

    print(
        f"Verification:        v{state['versions']['verification']} "
        f"{'[STALE]' if state['stale']['verification'] else '[CURRENT]'}"
    )

    verification_customer_dep = (
        state["dependencies"]["verification"]["customer_state_version"]
    )
    verification_product_dep = (
        state["dependencies"]["verification"]["product_matches_version"]
    )
    verification_solution_dep = (
        state["dependencies"]["verification"]["candidate_solutions_version"]
    )

    print(
        f"  based on Customer State v{verification_customer_dep}"
    )
    print(
        f"  based on Product Matches v{verification_product_dep}"
    )
    print(
        f"  based on Candidate Solutions v{verification_solution_dep}"
    )

def print_json(title, data):
    if DEBUG:
        print(f"\n=== {title} ===")
        print(json.dumps(data, ensure_ascii=False, indent=2))

def print_requirement_summary(customer_state):
    print("\n[1] Requirement Identification Agent  OK")
    print(f"    Facts:        {len(customer_state['facts'])}")
    print(f"    Requirements: {len(customer_state['requirements'])}")
    print(f"    Constraints:  {len(customer_state['constraints'])}")
    print(f"    Preferences:  {len(customer_state['preferences'])}")
    print(f"    Unknowns:     {len(customer_state['unknowns'])}")

def print_product_summary(matched_products):
    matches = matched_products.get("matched_products", [])

    match_count = sum(
        1 for item in matches
        if item.get("match_type") == "match"
    )

    partial_count = sum(
        1 for item in matches
        if item.get("match_type") == "partial"
    )

    clarification_count = sum(
        1 for item in matches
        if item.get("match_type") == "requires_clarification"
    )

    print("\n[2] Product Search Agent              OK")
    print(f"    Product capabilities: {len(matches)}")
    print(f"    Match:                 {match_count}")
    print(f"    Partial:               {partial_count}")
    print(f"    Need clarification:    {clarification_count}")

def print_solution_summary(candidate_solutions, version=1):
    solutions = candidate_solutions.get("candidate_solutions", [])

    print(f"\n[3] Solution Matching Agent v{version}       OK")
    print(f"    Candidates: {len(solutions)}")

    for solution in solutions:
        print(f"    - {solution.get('solution_name', 'Unnamed solution')}")
        print(
            f"      Matched: {len(solution.get('matched_needs', []))}, "
            f"Partial: {len(solution.get('partial_matches', []))}, "
            f"Unresolved: {len(solution.get('unresolved_items', []))}"
        )

def print_verification_summary(verification, version=1):
    status = verification.get("verification_status", "unknown")
    issues = verification.get("issues", [])

    print(f"\n[4] Verification Agent v{version}")
    print(f"    Status: {status.upper()}")
    print(f"    Issues: {len(issues)}")

    for issue in issues:
        severity = issue.get("severity", "").upper()
        issue_type = issue.get("issue_type", "")
        print(f"    [{severity}] {issue_type}")

def print_supervisor_summary(supervisor_decision, version=1):
    next_agent = supervisor_decision.get("next_agent", "UNKNOWN")

    print(f"\n[5] Supervisor Agent v{version}")
    print(f"    Next: {next_agent}")

def print_research_summary(research_findings):
    print("\n[7] Research Agent                    OK")
    print(f"    Findings:      {len(research_findings['findings'])}")
    print(f"    Opportunities: {len(research_findings['opportunities'])}")
    print(f"    Risks:         {len(research_findings['risks'])}")
    print(f"    Questions:     {len(research_findings['questions'])}")
