"""
监控工具

监控系统指标，检测异常情况。
"""

from __future__ import annotations

from typing import Any, Dict, List

from .base_tool import BaseTool


class MonitorTool(BaseTool):
    """监控工具"""

    @property
    def name(self) -> str:
        return "monitor_tool"

    @property
    def description(self) -> str:
        return "监控系统指标，检测异常情况（如多样性过低、覆盖率不足等）"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要监控的指标列表，如 ['diversity', 'coverage', 'precision@5']",
                },
                "thresholds": {
                    "type": "object",
                    "description": "指标阈值，如 {'diversity': 0.4, 'coverage': 0.3}",
                },
            },
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["healthy", "warning", "critical"]},
                "metrics": {"type": "object", "description": "当前指标值"},
                "anomalies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "metric": {"type": "string"},
                            "current_value": {"type": "number"},
                            "threshold": {"type": "number"},
                            "severity": {"type": "string"},
                        },
                    },
                },
            },
        }

    def _execute(self, **kwargs) -> Any:
        """执行监控"""
        from myutils.evaluation import evaluate_recommenders

        metrics_to_monitor = kwargs.get("metrics", ["diversity", "coverage", "precision@5"])
        thresholds = kwargs.get("thresholds", {
            "diversity": 0.4,
            "coverage": 0.3,
            "precision@5": 0.2,
        })

        # 执行评估获取当前指标
        eval_result = evaluate_recommenders(top_k=5)

        # 提取 ppo_rerank 算法的指标
        ppo_metrics = None
        for metric in eval_result.get("metrics", []):
            if metric["algorithm"] == "ppo_rerank":
                ppo_metrics = metric
                break

        if not ppo_metrics:
            return {
                "status": "warning",
                "metrics": {},
                "anomalies": [{
                    "metric": "model_status",
                    "current_value": 0,
                    "threshold": 1,
                    "severity": "warning",
                    "message": "未找到 PPO 模型评估结果",
                }],
            }

        # 检测异常
        anomalies = []
        current_metrics = {
            "diversity": ppo_metrics.get("diversity", 0),
            "coverage": ppo_metrics.get("coverage", 0),
            "precision@5": ppo_metrics.get("precision_at_k", 0),
            "recall@5": ppo_metrics.get("recall_at_k", 0),
            "ndcg@5": ppo_metrics.get("ndcg_at_k", 0),
        }

        for metric_name in metrics_to_monitor:
            current_value = current_metrics.get(metric_name, 0)
            threshold = thresholds.get(metric_name)

            if threshold is not None and current_value < threshold:
                severity = "critical" if current_value < threshold * 0.8 else "warning"
                anomalies.append({
                    "metric": metric_name,
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity,
                    "message": f"{metric_name} 低于阈值 {threshold}",
                })

        # 确定整体状态
        if any(a["severity"] == "critical" for a in anomalies):
            status = "critical"
        elif anomalies:
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "metrics": current_metrics,
            "anomalies": anomalies,
        }
