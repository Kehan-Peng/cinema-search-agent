"""
工具基类

所有 Agent 工具必须继承此基类，提供统一的调用接口、参数验证、异常处理等能力。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class ToolStatus(str, Enum):
    """工具执行状态"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ToolResult:
    """工具执行结果"""
    status: ToolStatus
    output: Any
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata or {},
        }


class BaseTool(ABC):
    """
    工具基类

    所有工具必须实现：
    - name: 工具名称（唯一标识）
    - description: 工具描述（用于 Agent 理解工具用途）
    - input_schema: 输入参数 schema
    - output_schema: 输出结果 schema
    - execute: 执行逻辑
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称（唯一标识）"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """
        输入参数 schema

        示例：
        {
            "type": "object",
            "properties": {
                "pages": {"type": "integer", "description": "爬取页数"},
                "download_covers": {"type": "boolean", "description": "是否下载封面"}
            },
            "required": ["pages"]
        }
        """
        pass

    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """
        输出结果 schema

        示例：
        {
            "type": "object",
            "properties": {
                "total_movies": {"type": "integer"},
                "downloaded_covers": {"type": "integer"}
            }
        }
        """
        pass

    def validate_input(self, **kwargs) -> bool:
        """
        验证输入参数

        默认实现：检查 required 字段是否存在
        子类可覆盖此方法实现更复杂的验证逻辑
        """
        required_fields = self.input_schema.get("required", [])
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(f"缺少必需参数: {field}")
        return True

    @abstractmethod
    def _execute(self, **kwargs) -> Any:
        """
        工具执行逻辑（子类实现）

        返回执行结果（任意类型）
        """
        pass

    def execute(self, **kwargs) -> ToolResult:
        """
        执行工具（带异常处理和计时）

        Args:
            **kwargs: 工具输入参数

        Returns:
            ToolResult: 执行结果
        """
        start_time = datetime.now()

        try:
            # 验证输入
            self.validate_input(**kwargs)

            # 执行工具
            output = self._execute(**kwargs)

            # 计算耗时
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=output,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return ToolResult(
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
                duration_ms=duration_ms,
            )

    def rollback(self) -> bool:
        """
        回滚操作（可选）

        某些工具支持回滚（如数据库操作、文件修改等）
        默认实现：不支持回滚
        """
        return False
