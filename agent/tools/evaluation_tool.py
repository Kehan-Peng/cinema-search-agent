"""
评估工具

执行离线评估，计算推荐算法的 precision@k、recall@k、ndcg@k、coverage、diversity 等指标。
"""

from __future__ import annotations

from typing import Any, Dict

from .base_tool import BaseTool


class EvaluationTool(BaseTool):
    """评估工具"""

    @property
    def name(self) -> str:
        return "evaluation_tool"

    @property
    def description(self) -> str:
        return "执行离线评估，计算推荐算法的 precision@k、recall@k、ndcg@k、coverage、diversity 等指标"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "top_k": {
                    "type": "integer",
                    "description": "评估的推荐列表长度",
                    "default": 5,
                    "minimum": 1,
                },
                "algorithms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要评估的算法列表，为空则评估所有算法",
                },
            },
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "sample_users": {"type": "integer", "description": "评估用户数"},
                "top_k": {"type": "integer", "description": "推荐列表长度"},
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "algorithm": {"type": "string"},
                            "precision_at_k": {"type": "number"},
                            "recall_at_k": {"type": "number"},
                            "ndcg_at_k": {"type": "number"},
                            "coverage": {"type": "number"},
                            "diversity": {"type": "number"},
                        },
                    },
                },
            },
        }

    def _execute(self, **kwargs) -> Any:
        """执行评估"""
        from myutils.evaluation import evaluate_recommenders

        top_k = kwargs.get("top_k", 5)
        algorithms = kwargs.get("algorithms")

        # 执行评估
        result = evaluate_recommenders(top_k=top_k)

        # 如果指定了算法列表，则过滤结果
        if algorithms:
            result["metrics"] = [
                metric for metric in result["metrics"]
                if metric["algorithm"] in algorithms
            ]

        return result
