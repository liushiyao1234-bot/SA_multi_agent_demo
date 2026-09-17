
from datetime import datetime


class ToolTrace:
    def __init__(self):
        self.records = []

    def record(
        self,
        agent_name,
        tool_name,
        arguments,
        success,
        duration_ms,
        result_count=None,
        error=None,
    ):
        self.records.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent_name": agent_name,
            "tool_name": tool_name,
            "arguments": arguments,
            "success": success,
            "duration_ms": duration_ms,
            "result_count": result_count,
            "error": error,
        })

    def get_records(self):
        return self.records