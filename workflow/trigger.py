"""Single deterministic scheduler for freshness and semantic routing."""

# from agents.product_search import build_product_search_context, product_search_agent
from agents.product_search import (
    build_product_search_context,
    plan_product_queries,
    analyze_product_matches,
)
from agents.requirement import requirement_identification_agent
from agents.solution import correct_solution, solution_matching_agent
from agents.supervisor import supervisor_agent
from agents.verification import verification_agent
from llm import parse_json_response
from utils.output import (
    print_product_summary,
    print_requirement_summary,
    print_solution_summary,
    print_supervisor_summary,
    print_verification_summary,
)
from workflow.state import (
    invalidate_supervisor_decision,
    mark_downstream_stale,
    refresh_stale_flags,
)


AGENT_REQUIREMENT = "Requirement Identification Agent"
AGENT_PRODUCT = "Product Search Agent"
AGENT_SOLUTION = "Solution Matching Agent"
AGENT_VERIFICATION = "Verification Agent"
AGENT_SUPERVISOR = "Supervisor Agent"
END = "END"


def determine_restart_point(state):
    """Compatibility API: return the earliest missing or stale stage."""
    refresh_stale_flags(state)
    if state.get("customer_state") is None:
        return AGENT_REQUIREMENT
    if state["stale"]["product_matches"]:
        return AGENT_PRODUCT
    if state["stale"]["candidate_solutions"]:
        return AGENT_SOLUTION
    if state["stale"]["verification"]:
        return AGENT_VERIFICATION
    return END


def determine_next_action(state):
    """Choose one next action, with freshness always taking priority."""
    restart_point = determine_restart_point(state)
    if restart_point != END:
        return {
            "action_type": "recalculate",
            "next_agent": restart_point,
            "reason": (
                f"{restart_point} output is missing, stale, "
                "or dependency-mismatched."
            ),
        }

    decision = state.get("supervisor_decision")
    decision_version = state.get("supervisor_decision_verification_version")
    current_verification_version = state["versions"]["verification"]
    if decision is None or decision_version != current_verification_version:
        return {
            "action_type": "supervise",
            "next_agent": AGENT_SUPERVISOR,
            "reason": (
                "All derived data are current; evaluate the latest verification."
            ),
        }

    next_agent = decision.get("next_agent", END)
    if next_agent == END:
        return {
            "action_type": "end",
            "next_agent": END,
            "reason": decision.get("reason", "Supervisor ended the workflow."),
        }

    if next_agent not in {AGENT_REQUIREMENT, AGENT_PRODUCT, AGENT_SOLUTION}:
        raise ValueError(f"Supervisor returned unsupported next_agent: {next_agent!r}")

    return {
        "action_type": "correct",
        "next_agent": next_agent,
        "reason": decision.get(
            "reason", "Supervisor requested semantic correction."
        ),
    }


def _store_product_matches(state, value):
    state["product_matches"] = parse_json_response(value)
    state["versions"]["product_matches"] += 1
    state["stale"]["product_matches"] = False
    state["dependencies"]["product_matches"]["customer_state_version"] = (
        state["versions"]["customer_state"]
    )
    mark_downstream_stale(state, "product_matches")


def _store_candidate_solutions(state, value):
    state["candidate_solutions"] = parse_json_response(value)
    state["versions"]["candidate_solutions"] += 1
    state["stale"]["candidate_solutions"] = False
    dependencies = state["dependencies"]["candidate_solutions"]
    dependencies["customer_state_version"] = state["versions"]["customer_state"]
    dependencies["product_matches_version"] = state["versions"]["product_matches"]
    mark_downstream_stale(state, "candidate_solutions")


def _store_verification(state, value):
    state["verification"] = parse_json_response(value)
    state["versions"]["verification"] += 1
    state["stale"]["verification"] = False
    dependencies = state["dependencies"]["verification"]
    dependencies["customer_state_version"] = state["versions"]["customer_state"]
    dependencies["product_matches_version"] = state["versions"]["product_matches"]
    dependencies["candidate_solutions_version"] = (
        state["versions"]["candidate_solutions"]
    )
    invalidate_supervisor_decision(state)


def run_requirement(state):
    state["customer_state"] = parse_json_response(
        requirement_identification_agent(state["customer_input"])
    )
    state["versions"]["customer_state"] += 1
    mark_downstream_stale(state, "customer_state")
    print_requirement_summary(state["customer_state"])
    return state


def run_product_search(state, products, executor):
    search_context = build_product_search_context(
        state["customer_state"]
    )

    # 1. Product Search Agent 规划检索词
    query_plan_result = plan_product_queries(search_context)
    query_plan = parse_json_response(query_plan_result)

    print("\n=== Product Search Query Plan ===")

    retrieved_capabilities = []

    # 2. Harness 执行 Tool
    for item in query_plan["queries"]:
        query = item["query"]
        reason = item.get("reason", "")

        print(f"- {query} | {reason}")

        results = executor.execute(
            agent_name=AGENT_PRODUCT,
            tool_name="search_product_capabilities",
            query=query,
            products=products,
        )

        retrieved_capabilities.extend(results)

    # 3. Tool结果去重
    unique_capabilities = []
    seen = set()

    for item in retrieved_capabilities:
        key = (
            item.get("product"),
            item.get("category"),
            item.get("capability"),
        )

        if key not in seen:
            seen.add(key)
            unique_capabilities.append(item)

    # 4. Product Search Agent根据检索证据做最终匹配
    result = analyze_product_matches(
        search_context,
        unique_capabilities,
    )

    _store_product_matches(state, result)
    print_product_summary(state["product_matches"])

    return state


def run_solution(state, correction=False):
    if correction:
        result = correct_solution(
            state["customer_state"],
            state["product_matches"],
            state["candidate_solutions"],
            state["verification"],
        )
    else:
        result = solution_matching_agent(
            state["customer_state"], state["product_matches"]
        )
    _store_candidate_solutions(state, result)
    print_solution_summary(
        state["candidate_solutions"],
        state["versions"]["candidate_solutions"],
    )
    return state


def run_verification(state):
    result = verification_agent(
        state["customer_state"],
        state["product_matches"],
        state["candidate_solutions"],
    )
    _store_verification(state, result)
    print_verification_summary(
        state["verification"], state["versions"]["verification"]
    )
    return state


def run_supervisor(state):
    state["supervisor_decision"] = parse_json_response(
        supervisor_agent(state["verification"])
    )
    state["versions"]["supervisor_decision"] = (
        state["versions"].get("supervisor_decision", 0) + 1
    )
    state["supervisor_decision_verification_version"] = (
        state["versions"]["verification"]
    )
    print_supervisor_summary(
        state["supervisor_decision"],
        state["versions"]["supervisor_decision"],
    )
    return state


def execute_action(state, products, executor, action):
    """Execute one action, update State, and return control to scheduler."""
    next_agent = action["next_agent"]
    action_type = action["action_type"]

    if next_agent == AGENT_REQUIREMENT:
        return run_requirement(state)
    if next_agent == AGENT_PRODUCT:
        return run_product_search(state, products, executor)
    if next_agent == AGENT_SOLUTION:
        return run_solution(state, correction=action_type == "correct")
    if next_agent == AGENT_VERIFICATION:
        return run_verification(state)
    if next_agent == AGENT_SUPERVISOR:
        return run_supervisor(state)
    if next_agent == END:
        return state
    raise ValueError(f"No executor registered for {next_agent!r}")


def run_scheduler(
    state,
    products,
    executor,
    max_steps=20,
    max_semantic_corrections=3,
):
    """Run one action at a time until the Supervisor returns END."""

    scheduler_state = state.setdefault("scheduler", {})

    # 每一轮 scheduler 独立计数
    scheduler_state.update(
        last_action=None,
        last_reason=None,
        steps=0,
        semantic_corrections=0,
        blocked=False,
    )

    for _ in range(max_steps):
        action = determine_next_action(state)

        # 只限制 Supervisor 发起的语义整改。
        # stale / dependency 引起的正常重算不计数。
        if action["action_type"] == "correct":
            scheduler_state["semantic_corrections"] += 1

            if (
                scheduler_state["semantic_corrections"]
                > max_semantic_corrections
            ):
                scheduler_state["blocked"] = True

                print("\n=== Scheduler Guard ===")
                print(
                    "Semantic correction limit reached. "
                    "Workflow paused to avoid repeated Agent loops."
                )

                return state

        scheduler_state.update(
            last_action=action["action_type"],
            last_reason=action["reason"],
            steps=scheduler_state["steps"] + 1,
        )

        if action["action_type"] == "end":
            return state

        execute_action(
            state,
            products,
            executor,
            action,
        )

    raise RuntimeError(
        f"Scheduler did not reach END within {max_steps} steps; "
        "check repeated Supervisor correction routing."
    )


def run_stale_recalculation(state, products, executor):
    """Compatibility wrapper; recalculation now uses the unified scheduler."""
    return run_scheduler(state, products, executor)
