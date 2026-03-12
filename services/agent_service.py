"""
Agent 服务

提供 Agent 系统的服务层接口，供后台管理系统调用。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.agent_core import AgentCore
from agent.tool_registry import ToolRegistry
from agent.tools.crawler_tool import CrawlerTool
from agent.tools.evaluation_tool import EvaluationTool
from agent.tools.monitor_tool import MonitorTool
from agent.tools.training_tool import TrainingTool


class AgentService:
    """Agent 服务"""

    def __init__(self):
        # 创建工具注册中心
        self.registry = ToolRegistry()

        # 注册工具
        self.registry.register(CrawlerTool())
        self.registry.register(EvaluationTool())
        self.registry.register(TrainingTool())
        self.registry.register(MonitorTool())

        # 创建 Agent
        self.agent = AgentCore(tool_registry=self.registry)

    def execute_goal(self, goal: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行目标

        Args:
            goal: 目标描述
            context: 上下文信息

        Returns:
            执行结果
        """
        result = self.agent.execute_goal(goal, context)
        return result.to_dict()

    def monitor_system_health(self) -> Dict[str, Any]:
        """
        监控系统健康状态

        Returns:
            健康状态报告
        """
        return self.agent.monitor_system_health()

    def get_status(self) -> Dict[str, Any]:
        """
        获取 Agent 状态

        Returns:
            状态信息
        """
        return self.agent.get_status()

    def list_tools(self) -> List[Dict[str, str]]:
        """
        列出所有工具

        Returns:
            工具列表
        """
        return self.registry.list_tools()

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的决策记录

        Args:
            limit: 返回条数

        Returns:
            决策记录列表
        """
        return self.agent.action_log.get_recent_decisions(limit)

    def get_action_stats(self) -> Dict[str, Any]:
        """
        获取工具调用统计

        Returns:
            统计信息
        """
        return self.agent.action_log.get_action_stats()
