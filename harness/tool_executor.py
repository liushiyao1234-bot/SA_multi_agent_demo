
import time


class ToolExecutor:
    def __init__(self, registry):
        self.registry = registry

    def execute(self, agent_name, tool_name, **kwargs):
        # 1. 从 Registry 获取 Tool
        tool = self.registry.get(tool_name)

        # 2. 检查 Agent 是否有权限调用
        if not self.registry.is_allowed(tool_name, agent_name):
            raise PermissionError(
                f"Agent '{agent_name}' is not allowed to use tool '{tool_name}'"
            )

        # 3. 获取真正的 Python function
        func = tool["func"]

        # 4. 执行 Tool
        try:
            result = func(**kwargs)
        except Exception as e:
            raise RuntimeError(
                f"Tool '{tool_name}' execution failed: {e}"
            ) from e

        # 5. 返回结果
        return result



class ToolExecutor:
    def __init__(self, registry, trace=None):
        self.registry = registry
        self.trace = trace

    def execute(self, agent_name, tool_name, **kwargs):
        tool = self.registry.get(tool_name)

        if not self.registry.is_allowed(tool_name, agent_name):
            raise PermissionError(
                f"Agent '{agent_name}' is not allowed to use tool '{tool_name}'"
            )

        func = tool["func"]
        start = time.perf_counter()

        try:
            result = func(**kwargs)

            duration_ms = round(
                (time.perf_counter() - start) * 1000,
                2
            )

            if self.trace:
                result_count = (
                    len(result)
                    if isinstance(result, (list, dict))
                    else None
                )

                self.trace.record(
                    agent_name=agent_name,
                    tool_name=tool_name,
                    arguments=kwargs,
                    success=True,
                    duration_ms=duration_ms,
                    result_count=result_count,
                )

            return result

        except Exception as e:
            duration_ms = round(
                (time.perf_counter() - start) * 1000,
                2
            )

            if self.trace:
                self.trace.record(
                    agent_name=agent_name,
                    tool_name=tool_name,
                    arguments=kwargs,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(e),
                )

            raise RuntimeError(
                f"Tool '{tool_name}' execution failed: {e}"
            ) from e