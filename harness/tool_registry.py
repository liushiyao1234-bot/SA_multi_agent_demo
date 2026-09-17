
# 在product search agent试图调用product检索能力前，tool registry先做一道验证：tool是否存在？agent是否有权限调用？等等
# 避免全靠agent prompt里的文字性描述限制边界，改用代码控制
class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, func, allowed_agents=None):
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        self._tools[name] = {
            "func": func,
            "allowed_agents": allowed_agents or []
        }

    def get(self, name):
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")

        return self._tools[name]

    def list_tools(self):
        return list(self._tools.keys())

    def is_allowed(self, tool_name, agent_name):
        tool = self.get(tool_name)

        allowed_agents = tool["allowed_agents"]

        if not allowed_agents:
            return True

        return agent_name in allowed_agents