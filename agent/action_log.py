"""
Agent 行为日志

记录 Agent 每次决策、工具调用详情，支持决策回溯与分析。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ActionLog:
    """Agent 行为日志"""

    def __init__(self, log_dir: Optional[Path] = None):
        """
        初始化行为日志

        Args:
            log_dir: 日志目录，默认为 runtime/agent/logs
        """
        if log_dir is None:
            log_dir = Path(__file__).resolve().parents[1] / "runtime" / "agent" / "logs"

        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 当前会话日志文件
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{self.session_id}.jsonl"

    def log_decision(
        self,
        goal: str,
        plan: List[str],
        actions: List[Dict[str, Any]],
        result: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        记录一次完整的决策

        Args:
            goal: 目标
            plan: 执行计划
            actions: 工具调用列表
            result: 执行结果
            metadata: 额外元数据
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "goal": goal,
            "plan": plan,
            "actions": actions,
            "result": result,
            "metadata": metadata or {},
        }

        self._write_log(log_entry)

    def log_action(
        self,
        tool_name: str,
        input_params: Dict[str, Any],
        output: Any,
        status: str,
        duration_ms: int,
        error: Optional[str] = None,
    ) -> None:
        """
        记录单个工具调用

        Args:
            tool_name: 工具名称
            input_params: 输入参数
            output: 输出结果
            status: 执行状态
            duration_ms: 耗时（毫秒）
            error: 错误信息
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "type": "action",
            "tool": tool_name,
            "input": input_params,
            "output": output,
            "status": status,
            "duration_ms": duration_ms,
            "error": error,
        }

        self._write_log(log_entry)

    def _write_log(self, log_entry: Dict[str, Any]) -> None:
        """
        写入日志文件

        Args:
            log_entry: 日志条目
        """
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def read_session_logs(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        读取会话日志

        Args:
            session_id: 会话 ID，None 表示当前会话

        Returns:
            日志条目列表
        """
        if session_id is None:
            session_id = self.session_id

        log_file = self.log_dir / f"session_{session_id}.jsonl"
        if not log_file.exists():
            return []

        logs = []
        with log_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))

        return logs

    def list_sessions(self) -> List[str]:
        """
        列出所有会话

        Returns:
            会话 ID 列表
        """
        sessions = []
        for log_file in self.log_dir.glob("session_*.jsonl"):
            session_id = log_file.stem.replace("session_", "")
            sessions.append(session_id)

        return sorted(sessions, reverse=True)

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的决策记录

        Args:
            limit: 返回条数

        Returns:
            决策记录列表
        """
        logs = self.read_session_logs()
        decisions = [log for log in logs if log.get("type") != "action"]
        return decisions[-limit:]

    def get_action_stats(self) -> Dict[str, Any]:
        """
        获取工具调用统计

        Returns:
            统计信息
        """
        logs = self.read_session_logs()
        actions = [log for log in logs if log.get("type") == "action"]

        if not actions:
            return {
                "total_calls": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0,
                "tool_usage": {},
            }

        total_calls = len(actions)
        success_calls = sum(1 for action in actions if action.get("status") == "success")
        total_duration = sum(action.get("duration_ms", 0) for action in actions)

        tool_usage = {}
        for action in actions:
            tool_name = action.get("tool", "unknown")
            tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

        return {
            "total_calls": total_calls,
            "success_rate": round(success_calls / total_calls, 4),
            "avg_duration_ms": round(total_duration / total_calls, 2),
            "tool_usage": tool_usage,
        }
