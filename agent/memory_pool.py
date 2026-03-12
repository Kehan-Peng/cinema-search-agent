"""
全局状态池

维护系统全局状态，存储历史决策与结果，提供状态查询接口。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


class MemoryPool:
    """全局状态池"""

    def __init__(self):
        # 指标状态
        self._metrics: Dict[str, float] = {}

        # 数据状态
        self._data_stats: Dict[str, int] = {}

        # 模型状态
        self._model_state: Dict[str, Any] = {}

        # 资源状态
        self._resource_state: Dict[str, Any] = {}

        # 历史决策
        self._decision_history: List[Dict] = []

    def update_metrics(self, metrics: Dict[str, float]) -> None:
        """
        更新指标状态

        Args:
            metrics: 指标字典，如 {"precision@5": 0.45, "diversity": 0.52}
        """
        self._metrics.update(metrics)

    def get_metrics(self, metric_names: Optional[List[str]] = None) -> Dict[str, float]:
        """
        获取指标状态

        Args:
            metric_names: 指标名称列表，None 表示全部

        Returns:
            指标字典
        """
        if metric_names is None:
            return self._metrics.copy()
        return {name: self._metrics.get(name, 0.0) for name in metric_names}

    def update_data_stats(self, stats: Dict[str, int]) -> None:
        """
        更新数据状态

        Args:
            stats: 数据统计，如 {"total_movies": 250, "total_comments": 5000}
        """
        self._data_stats.update(stats)

    def get_data_stats(self) -> Dict[str, int]:
        """获取数据状态"""
        return self._data_stats.copy()

    def update_model_state(self, state: Dict[str, Any]) -> None:
        """
        更新模型状态

        Args:
            state: 模型状态，如 {"version": "v1.2", "training": False}
        """
        self._model_state.update(state)

    def get_model_state(self) -> Dict[str, Any]:
        """获取模型状态"""
        return self._model_state.copy()

    def update_resource_state(self, state: Dict[str, Any]) -> None:
        """
        更新资源状态

        Args:
            state: 资源状态，如 {"db_connected": True, "cache_available": True}
        """
        self._resource_state.update(state)

    def get_resource_state(self) -> Dict[str, Any]:
        """获取资源状态"""
        return self._resource_state.copy()

    def record_decision(self, goal: str, plan: List[str], result: str) -> None:
        """
        记录决策

        Args:
            goal: 目标
            plan: 执行计划
            result: 执行结果
        """
        self._decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "goal": goal,
            "plan": plan,
            "result": result,
        })

    def get_decision_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取决策历史

        Args:
            limit: 返回最近 N 条记录，None 表示全部

        Returns:
            决策历史列表
        """
        if limit is None:
            return self._decision_history
        return self._decision_history[-limit:]

    def get_global_state(self) -> Dict[str, Any]:
        """
        获取全局状态快照

        Returns:
            包含所有状态的字典
        """
        return {
            "metrics": self._metrics,
            "data_stats": self._data_stats,
            "model_state": self._model_state,
            "resource_state": self._resource_state,
            "last_decision": self._decision_history[-1] if self._decision_history else None,
        }

    def clear_history(self) -> None:
        """清空决策历史"""
        self._decision_history.clear()
