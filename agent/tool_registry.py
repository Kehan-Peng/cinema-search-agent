"""
工具注册中心

管理所有可调用工具，提供工具发现、查询、调用等能力。
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .tools.base_tool import BaseTool, ToolResult


class ToolRegistry:
    """工具注册中心"""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._call_history: List[Dict] = []

    def register(self, tool: BaseTool) -> None:
        """
        注册工具

        Args:
            tool: 工具实例
        """
        if tool.name in self._tools:
            raise ValueError(f"工具已存在: {tool.name}")
        self._tools[tool.name] = tool

    def unregister(self, tool_name: str) -> None:
        """
        注销工具

        Args:
            tool_name: 工具名称
        """
        if tool_name not in self._tools:
            raise ValueError(f"工具不存在: {tool_name}")
        del self._tools[tool_name]

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取工具实例

        Args:
            tool_name: 工具名称

        Returns:
            工具实例，不存在则返回 None
        """
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, str]]:
        """
        列出所有工具

        Returns:
            工具列表 [{"name": "...", "description": "..."}, ...]
        """
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]

    def call_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        调用工具

        Args:
            tool_name: 工具名称
            **kwargs: 工具参数

        Returns:
            ToolResult: 执行结果
        """
        from .tools.base_tool import ToolStatus

        tool = self.get_tool(tool_name)
        if tool is None:
            return ToolResult(
                status=ToolStatus.FAILED,
                output=None,
                error=f"工具不存在: {tool_name}",
            )

        # 执行工具
        result = tool.execute(**kwargs)

        # 记录调用历史
        self._call_history.append({
            "tool_name": tool_name,
            "input": kwargs,
            "result": result.to_dict(),
        })

        return result

    def get_call_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取工具调用历史

        Args:
            limit: 返回最近 N 条记录，None 表示全部

        Returns:
            调用历史列表
        """
        if limit is None:
            return self._call_history
        return self._call_history[-limit:]

    def clear_history(self) -> None:
        """清空调用历史"""
        self._call_history.clear()
