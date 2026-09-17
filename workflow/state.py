"""Workflow state creation, dependency tracking, and invalidation."""


DERIVED_COMPONENTS = (
    "product_matches",
    "candidate_solutions",
    "verification",
)


def create_initial_state(customer_input):
    return {
        "customer_input": customer_input,
        "customer_state": None,
        "meeting_record": None,
        "research_findings": None,
        "product_matches": None,
        "candidate_solutions": None,
        "verification": None,
        "supervisor_decision": None,
        "supervisor_decision_verification_version": None,
        "dependencies": {
            "product_matches": {"customer_state_version": None},
            "candidate_solutions": {
                "customer_state_version": None,
                "product_matches_version": None,
            },
            "verification": {
                "customer_state_version": None,
                "product_matches_version": None,
                "candidate_solutions_version": None,
            },
        },
        "versions": {
            "customer_state": 0,
            "product_matches": 0,
            "candidate_solutions": 0,
            "verification": 0,
            "supervisor_decision": 0,
        },
        "stale": {
            "product_matches": True,
            "candidate_solutions": True,
            "verification": True,
        },
        "scheduler": {"last_action": None, "last_reason": None, "steps": 0},
    }


def invalidate_supervisor_decision(state):
    """Discard a routing decision whenever its verification input changes."""
    state["supervisor_decision"] = None
    state["supervisor_decision_verification_version"] = None


def mark_downstream_stale(state, changed_component):
    """Mark every derived result downstream of changed_component stale."""
    if changed_component == "customer_state":
        affected = DERIVED_COMPONENTS
    elif changed_component == "product_matches":
        affected = ("candidate_solutions", "verification")
    elif changed_component == "candidate_solutions":
        affected = ("verification",)
    else:
        affected = ()

    for component in affected:
        state["stale"][component] = True

    if affected or changed_component == "verification":
        invalidate_supervisor_decision(state)


def refresh_stale_flags(state):
    """Derive freshness from missing data and recorded dependency versions."""
    versions = state["versions"]
    dependencies = state["dependencies"]
    stale = state["stale"]

    if (
        state.get("product_matches") is None
        or dependencies["product_matches"]["customer_state_version"]
        != versions["customer_state"]
    ):
        stale["product_matches"] = True

    if (
        stale["product_matches"]
        or state.get("candidate_solutions") is None
        or dependencies["candidate_solutions"]["customer_state_version"]
        != versions["customer_state"]
        or dependencies["candidate_solutions"]["product_matches_version"]
        != versions["product_matches"]
    ):
        stale["candidate_solutions"] = True

    if (
        stale["candidate_solutions"]
        or state.get("verification") is None
        or dependencies["verification"]["customer_state_version"]
        != versions["customer_state"]
        or dependencies["verification"]["product_matches_version"]
        != versions["product_matches"]
        or dependencies["verification"]["candidate_solutions_version"]
        != versions["candidate_solutions"]
    ):
        stale["verification"] = True

    return stale
