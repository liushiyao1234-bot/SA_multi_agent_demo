from harness.tool_registry import ToolRegistry
from harness.tool_executor import ToolExecutor
from harness.trace import ToolTrace
from tools.product_tools import (
    load_product_catalog,
    search_product_capabilities,
)


def create_harness():
    registry = ToolRegistry()
    trace = ToolTrace()

    registry.register(
        name="load_product_catalog",
        func=load_product_catalog,
        allowed_agents=["Product Search Agent"],
    )

    registry.register(
        name="search_product_capabilities",
        func=search_product_capabilities,
        allowed_agents=["Product Search Agent"],
    )

    executor = ToolExecutor(
        registry=registry,
        trace=trace,
    )

    return registry, executor, trace