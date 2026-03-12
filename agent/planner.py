"""
任务规划器

将顶层目标拆解为可执行的子任务序列。
"""

from __future__ import annotations

from typing import Dict, List, Optional


class SubTask:
    """子任务"""

    def __init__(self, name: str, tool: str, params: Dict, description: str = ""):
        self.name = name
        self.tool = tool
        self.params = params
        self.description = description

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "tool": self.tool,
            "params": self.params,
            "description": self.description,
        }


class ExecutionPlan:
    """执行计划"""

    def __init__(self, goal: str, tasks: List[SubTask]):
        self.goal = goal
        self.tasks = tasks

    def to_dict(self) -> Dict:
        return {
            "goal": self.goal,
            "tasks": [task.to_dict() for task in self.tasks],
        }


class Planner:
    """任务规划器"""

    def __init__(self):
        # 预定义的目标模板
        self._goal_templates = {
            "提升多样性": self._plan_improve_diversity,
            "提升覆盖率": self._plan_improve_coverage,
            "提升准确率": self._plan_improve_accuracy,
            "补充数据": self._plan_enrich_data,
            "系统健康检查": self._plan_health_check,
        }

    def plan(self, goal: str, context: Optional[Dict] = None) -> ExecutionPlan:
        """
        规划任务

        Args:
            goal: 目标描述
            context: 上下文信息（如当前指标、系统状态等）

        Returns:
            ExecutionPlan: 执行计划
        """
        context = context or {}

        # 匹配预定义模板
        for template_key, planner_func in self._goal_templates.items():
            if template_key in goal:
                return planner_func(context)

        # 默认规划：评估 → 分析 → 执行
        return self._default_plan(goal, context)

    def _plan_improve_diversity(self, context: Dict) -> ExecutionPlan:
        """规划：提升多样性"""
        tasks = [
            SubTask(
                name="评估当前多样性",
                tool="evaluation_tool",
                params={"top_k": 5, "algorithms": ["ppo_rerank"]},
                description="评估当前推荐算法的多样性指标",
            ),
            SubTask(
                name="调整多样性权重",
                tool="training_tool",
                params={"action": "train", "force": True},
                description="重新训练模型，增加多样性权重",
            ),
            SubTask(
                name="验证效果",
                tool="evaluation_tool",
                params={"top_k": 5, "algorithms": ["ppo_rerank"]},
                description="验证训练后的多样性指标是否提升",
            ),
        ]
        return ExecutionPlan(goal="提升推荐多样性", tasks=tasks)

    def _plan_improve_coverage(self, context: Dict) -> ExecutionPlan:
        """规划：提升覆盖率"""
        tasks = [
            SubTask(
                name="评估当前覆盖率",
                tool="evaluation_tool",
                params={"top_k": 5, "algorithms": ["ppo_rerank"]},
                description="评估当前推荐算法的覆盖率指标",
            ),
            SubTask(
                name="补充长尾电影数据",
                tool="crawler_tool",
                params={"task_type": "movies", "pages": 2, "download_covers": True},
                description="爬取更多电影数据，增加长尾覆盖",
            ),
            SubTask(
                name="重新训练模型",
                tool="training_tool",
                params={"action": "train", "force": True},
                description="基于新数据重新训练模型",
            ),
            SubTask(
                name="验证效果",
                tool="evaluation_tool",
                params={"top_k": 5, "algorithms": ["ppo_rerank"]},
                description="验证训练后的覆盖率指标是否提升",
            ),
        ]
        return ExecutionPlan(goal="提升推荐覆盖率", tasks=tasks)

    def _plan_improve_accuracy(self, context: Dict) -> ExecutionPlan:
        """规划：提升准确率"""
        tasks = [
            SubTask(
                name="评估当前准确率",
                tool="evaluation_tool",
                params={"top_k": 5},
                description="评估所有算法的准确率指标",
            ),
            SubTask(
                name="补充电影简介",
                tool="crawler_tool",
                params={"task_type": "summaries", "limit_movies": 30, "use_api": True},
                description="补充电影简介，增强语义召回能力",
            ),
            SubTask(
                name="重新训练模型",
                tool="training_tool",
                params={"action": "train", "force": True},
                description="基于更完整的数据重新训练模型",
            ),
            SubTask(
                name="验证效果",
                tool="evaluation_tool",
                params={"top_k": 5, "algorithms": ["ppo_rerank"]},
                description="验证训练后的准确率指标是否提升",
            ),
        ]
        return ExecutionPlan(goal="提升推荐准确率", tasks=tasks)

    def _plan_enrich_data(self, context: Dict) -> ExecutionPlan:
        """规划：补充数据"""
        tasks = [
            SubTask(
                name="爬取电影数据",
                tool="crawler_tool",
                params={"task_type": "movies", "pages": 8, "download_covers": True},
                description="爬取 Top250 电影数据及封面",
            ),
            SubTask(
                name="补充电影简介",
                tool="crawler_tool",
                params={"task_type": "summaries", "limit_movies": 50, "use_api": True},
                description="补充电影简介数据",
            ),
            SubTask(
                name="爬取评论数据",
                tool="crawler_tool",
                params={"task_type": "comments", "pages": 3, "limit_movies": 30},
                description="爬取电影评论数据",
            ),
        ]
        return ExecutionPlan(goal="补充系统数据", tasks=tasks)

    def _plan_health_check(self, context: Dict) -> ExecutionPlan:
        """规划：系统健康检查"""
        tasks = [
            SubTask(
                name="监控系统指标",
                tool="monitor_tool",
                params={
                    "metrics": ["diversity", "coverage", "precision@5"],
                    "thresholds": {"diversity": 0.4, "coverage": 0.3, "precision@5": 0.2},
                },
                description="检查系统关键指标是否正常",
            ),
            SubTask(
                name="检查模型状态",
                tool="training_tool",
                params={"action": "status"},
                description="检查模型版本和训练状态",
            ),
        ]
        return ExecutionPlan(goal="系统健康检查", tasks=tasks)

    def _default_plan(self, goal: str, context: Dict) -> ExecutionPlan:
        """默认规划"""
        tasks = [
            SubTask(
                name="评估当前状态",
                tool="evaluation_tool",
                params={"top_k": 5},
                description="评估当前推荐系统状态",
            ),
        ]
        return ExecutionPlan(goal=goal, tasks=tasks)

    def decompose_task(self, task: str) -> List[SubTask]:
        """
        拆解单个任务为更细粒度的子任务

        Args:
            task: 任务描述

        Returns:
            子任务列表
        """
        # 简单实现：直接返回单个任务
        # 未来可扩展为更复杂的拆解逻辑
        return [SubTask(name=task, tool="", params={}, description=task)]
