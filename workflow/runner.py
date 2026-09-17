"""End-to-end SA multi-agent workflow using one scheduler."""

from agents.meeting import meeting_record_agent
from agents.requirement import update_customer_state
from agents.research import research_agent
from llm import parse_json_response
from product_loader import load_products
from utils.output import (
    print_json,
    print_research_summary,
    print_state_summary,
)
from workflow.state import create_initial_state, mark_downstream_stale
from workflow.trigger import run_scheduler
from harness.setup import create_harness


DEFAULT_CUSTOMER_INPUT = """
客户计划在 Queretaro 建设新的 SPEI 业务系统。希望采用私有云部署，
并且更倾向 OPEX 商业模式。客户目前使用 Oracle 数据库，对 GaussDB
双活比较感兴趣。新系统希望在 2026 年底前上线。目前还不知道客户
具体需要本地高可用、同城双活还是跨数据中心双活，也没有确认 RPO 和 RTO。
"""

DEFAULT_MEETING_NOTES = """
客户确认新 SPEI 系统计划部署在 Queretaro。客户目前仍在使用 Oracle
数据库。客户表示希望了解 GaussDB 双活，但目前没有决定是否迁移数据库。
客户尚未确认 RPO 和 RTO。双方同意由客户在下一次会议提供当前 Oracle
版本和数据库规模。
"""

DEFAULT_RESEARCH_MATERIAL = """
Source: Bank Alpha Annual Report 2025
The bank stated that it plans to expand its digital payment business
and increase investment in technology infrastructure.

Source: Public news article
Bank Alpha is constructing a new data center in Queretaro.

Source: Technology conference interview
A bank executive mentioned that the company is evaluating hybrid cloud
and database modernization technologies.

Source: Industry article
Bank Alpha has historically used Oracle databases for several core systems.
"""


def run_initial_analysis(state, products, executor):
    """Compatibility helper: run the initial state through the scheduler."""
    run_scheduler(state, products, executor)
    print_state_summary(state)
    print_json("Customer State - Detail", state["customer_state"])
    print_json("Product Search Agent - Detail", state["product_matches"])
    print_json("Solution Matching Agent - Detail", state["candidate_solutions"])
    print_json("Verification Agent - Detail", state["verification"])
    print_json("Supervisor Agent - Detail", state["supervisor_decision"])
    return state


def apply_meeting_update(state, meeting_notes, products, executor):
    """Record new information, update State, then yield to the scheduler."""
    state["meeting_record"] = parse_json_response(meeting_record_agent(meeting_notes))
    record = state["meeting_record"]
    print("\n[6] Meeting Record Agent             OK")
    print(f"    Facts:          {len(record.get('facts', []))}")
    print(f"    Decisions:      {len(record.get('decisions', []))}")
    print(f"    Action items:   {len(record.get('action_items', []))}")
    print(f"    Open questions: {len(record.get('open_questions', []))}")

    state["customer_state"] = parse_json_response(
        update_customer_state(state["customer_state"], record)
    )
    state["versions"]["customer_state"] += 1
    mark_downstream_stale(state, "customer_state")

    updated = state["customer_state"]
    print("\nRequirement Identification Agent - UPDATE OK")
    for label, key in (
        ("Facts", "facts"),
        ("Requirements", "requirements"),
        ("Constraints", "constraints"),
        ("Preferences", "preferences"),
        ("Unknowns", "unknowns"),
        ("Conflicts", "conflicts"),
    ):
        print(f"    {label + ':':<14}{len(updated.get(key, []))}")

    print_state_summary(state)
    run_scheduler(state, products, executor)
    print_state_summary(state)
    return state


def run_research(state, research_material):
    result = research_agent(research_material)
    state["research_findings"] = parse_json_response(result)
    print_research_summary(state["research_findings"])
    print_json("Research Agent - Detail", state["research_findings"])
    return state


def run_workflow(
    customer_input=DEFAULT_CUSTOMER_INPUT,
    meeting_notes=DEFAULT_MEETING_NOTES,
    research_material=DEFAULT_RESEARCH_MATERIAL,
    products=None,
):
    state = create_initial_state(customer_input)
    products = products if products is not None else load_products()

    registry, executor, trace = create_harness()

    run_initial_analysis(state, products, executor)
    apply_meeting_update(state, meeting_notes, products, executor)
    run_research(state, research_material)


    print("\n=== Tool Trace ===")

    for record in trace.get_records():
        print(
            f"{record['agent_name']} -> "
            f"{record['tool_name']} | "
            f"{record['duration_ms']} ms | "
            f"results={record['result_count']} | "
            f"success={record['success']}"
        )

    return state

