"""Compatibility API and command-line entry point for the SA demo."""

from agents.meeting import meeting_record_agent
from agents.product_search import build_product_search_context, product_search_agent
from agents.requirement import (
    requirement_identification_agent,
    update_customer_state as requirement_update_agent,
)
from agents.research import research_agent
from agents.solution import (
    correct_solution as solution_correction_agent,
    solution_matching_agent,
)
from agents.supervisor import supervisor_agent
from agents.verification import verification_agent
from llm import call_glm, parse_json_response
from product_loader import load_products
from utils.output import *
from workflow.runner import run_workflow
from workflow.state import create_initial_state, mark_downstream_stale
from workflow.trigger import (
    determine_next_action,
    determine_restart_point,
    execute_action,
    run_scheduler,
    run_stale_recalculation,
)


if __name__ == "__main__":
    run_workflow()
