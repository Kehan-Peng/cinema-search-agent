"""
Agent 调度中枢

统一的 Agent 调度大脑，负责接收目标、规划任务、编排工具调用、监控执行状态。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from .action_log import ActionLog
from .memory_pool import MemoryPool
from .planner import ExecutionPlan, Planner
from .tool_registry import ToolRegistry
from .tools.base_tool import ToolResult, ToolStatus


class ExecutionResult:
    """执行结果"""

    def __init__(
        self,
        goal: str,
        plan: ExecutionPlan,
        actions: List[Dict[str, Any]],
        status: str,
        message: str,
    ):
        self.goal = goal
        self.plan = plan
        self.actions = actions
        self.status = status
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "plan": self.plan.to_dict(),
            "actions": self.actions,
            "status": self.status,
            "message": self.message,
        }


class AgentCore:
    """Agent 调度中枢"""

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        memory_pool: Optional[MemoryPool] = None,
        action_log: Optional[ActionLog] = None,
        planner: Optional[Planner] = None,
    ):
        self.tool_registry = tool_registry or ToolRegistry()
        self.memory_pool = memory_pool or MemoryPool()
        self.action_log = action_log or ActionLog()
        self.planner = planner or Planner()

    def execute_goal(self, goal: str, context: Optional[Dict] = None) -> ExecutionResult:
        """
        执行目标

        Args:
            goal: 目标描述
            context: 上下文信息

        Returns:
            ExecutionResult: 执行结果
        """
        print(f"\n🎯 目标: {goal}")

        # 1. 规划任务
        plan = self.planner.plan(goal, context or self.memory_pool.get_global_state())
        print(f"\n📋 执行计划:")
        for idx, task in enumerate(plan.tasks, 1):
            print(f"  {idx}. {task.name} ({task.tool})")

        # 2. 执行任务
        actions = []
        for idx, task in enumerate(plan.tasks, 1):
            print(f"\n⚙️  执行任务 {idx}/{len(plan.tasks)}: {task.name}")

            # 调用工具
            result = self.tool_registry.call_tool(task.tool, **task.params)

            # 记录行动
            status_value = result.status.value if hasattr(result.status, 'value') else str(result.status)
            action_record = {
                "task_name": task.name,
                "tool": task.tool,
                "input": task.params,
                "output": result.output,
                "status": status_value,
                "duration_ms": result.duration_ms,
                "error": result.error,
            }
            actions.append(action_record)

            # 记录到日志
            self.action_log.log_action(
                tool_name=task.tool,
                input_params=task.params,
                output=result.output,
                status=status_value,
                duration_ms=result.duration_ms or 0,
                error=result.error,
            )

            # 如果任务失败，终止执行
            if result.status != ToolStatus.SUCCESS:
                error_msg = f"任务失败: {task.name} - {result.error}"
                print(f"❌ {error_msg}")

                # 记录决策
                self.action_log.log_decision(
                    goal=goal,
                    plan=[t.name for t in plan.tasks],
                    actions=actions,
                    result=error_msg,
                )

                return ExecutionResult(
                    goal=goal,
                    plan=plan,
                    actions=actions,
                    status="failed",
                    message=error_msg,
                )

            print(f"✅ 完成: {task.name}")

        # 3. 汇总结果
        success_msg = f"成功完成目标: {goal}"
        print(f"\n✨ {success_msg}")

        # 记录决策
        self.action_log.log_decision(
            goal=goal,
            plan=[t.name for t in plan.tasks],
            actions=actions,
            result=success_msg,
        )

        # 更新记忆
        self.memory_pool.record_decision(
            goal=goal,
            plan=[t.name for t in plan.tasks],
            result=success_msg,
        )

        return ExecutionResult(
            goal=goal,
            plan=plan,
            actions=actions,
            status="success",
            message=success_msg,
        )

    def monitor_system_health(self) -> Dict[str, Any]:
        """
        监控系统健康状态

        Returns:
            健康状态报告
        """
        # 调用监控工具
        result = self.tool_registry.call_tool(
            "monitor_tool",
            metrics=["diversity", "coverage", "precision@5"],
            thresholds={"diversity": 0.4, "coverage": 0.3, "precision@5": 0.2},
        )

        if result.status == ToolStatus.SUCCESS:
            return result.output
        else:
            return {
                "status": "error",
                "message": result.error,
            }

    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        处理事件

        Args:
            event_type: 事件类型
            event_data: 事件数据
        """
        print(f"\n📢 收到事件: {event_type}")

        # 根据事件类型触发相应的目标
        if event_type == "metric_anomaly":
            metric_name = event_data.get("metric")
            if metric_name == "diversity":
                self.execute_goal("提升多样性")
            elif metric_name == "coverage":
                self.execute_goal("提升覆盖率")
            elif metric_name in ["precision@5", "recall@5", "ndcg@5"]:
                self.execute_goal("提升准确率")

        elif event_type == "data_update":
            print("数据已更新，建议重新训练模型")

        elif event_type == "model_degradation":
            print("模型性能下降，触发重新训练")
            self.execute_goal("提升准确率")

        else:
            print(f"未知事件类型: {event_type}")

    def get_status(self) -> Dict[str, Any]:
        """
        获取 Agent 状态

        Returns:
            状态信息
        """
        return {
            "registered_tools": len(self.tool_registry.list_tools()),
            "tools": self.tool_registry.list_tools(),
            "global_state": self.memory_pool.get_global_state(),
            "recent_decisions": self.memory_pool.get_decision_history(limit=5),
            "action_stats": self.action_log.get_action_stats(),
        }
