"""
训练工具

执行 PPO 模型训练、初始化、回滚等操作。
"""

from __future__ import annotations

from typing import Any, Dict

from .base_tool import BaseTool


class TrainingTool(BaseTool):
    """训练工具"""

    @property
    def name(self) -> str:
        return "training_tool"

    @property
    def description(self) -> str:
        return "执行 PPO 模型训练、初始化、回滚等操作"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["train", "bootstrap", "rollback", "status"],
                    "description": "操作类型：train=训练模型，bootstrap=初始化模型，rollback=回滚版本，status=查看状态",
                },
                "force": {
                    "type": "boolean",
                    "description": "是否强制训练（忽略样本数量检查）",
                    "default": False,
                },
                "version_tag": {
                    "type": "string",
                    "description": "回滚到的版本标签（仅 rollback 操作需要）",
                },
            },
            "required": ["action"],
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string"},
                "status": {"type": "string"},
                "message": {"type": "string"},
                "model_version": {"type": "string"},
                "metrics": {"type": "object"},
            },
        }

    def _execute(self, **kwargs) -> Any:
        """执行训练操作"""
        from myutils.rl.local_ppo import (
            bootstrap_model,
            train_model,
            rollback_model,
            get_model_status,
        )

        action = kwargs["action"]

        if action == "train":
            force = kwargs.get("force", False)
            result = train_model(force=force)

            return {
                "action": "train",
                "status": "success" if result.get("success") else "failed",
                "message": result.get("message", "训练完成"),
                "model_version": result.get("version_tag"),
                "metrics": result.get("metrics", {}),
            }

        elif action == "bootstrap":
            result = bootstrap_model()

            return {
                "action": "bootstrap",
                "status": "success" if result.get("success") else "failed",
                "message": result.get("message", "初始化完成"),
                "model_version": result.get("version_tag"),
                "metrics": {},
            }

        elif action == "rollback":
            version_tag = kwargs.get("version_tag")
            if not version_tag:
                raise ValueError("回滚操作需要指定 version_tag")

            result = rollback_model(version_tag)

            return {
                "action": "rollback",
                "status": "success" if result.get("success") else "failed",
                "message": result.get("message", f"已回滚到版本 {version_tag}"),
                "model_version": version_tag,
                "metrics": {},
            }

        elif action == "status":
            status = get_model_status()

            return {
                "action": "status",
                "status": "success",
                "message": "获取状态成功",
                "model_version": status.get("active_version"),
                "metrics": status.get("metrics", {}),
            }

        else:
            raise ValueError(f"不支持的操作类型: {action}")
