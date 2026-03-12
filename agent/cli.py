"""
Agent CLI 命令行工具

提供命令行接口，方便测试和使用 Agent 系统。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agent.agent_core import AgentCore
from agent.tool_registry import ToolRegistry
from agent.tools.crawler_tool import CrawlerTool
from agent.tools.evaluation_tool import EvaluationTool
from agent.tools.monitor_tool import MonitorTool
from agent.tools.training_tool import TrainingTool


def init_agent() -> AgentCore:
    """初始化 Agent"""
    # 创建工具注册中心
    registry = ToolRegistry()

    # 注册工具
    registry.register(CrawlerTool())
    registry.register(EvaluationTool())
    registry.register(TrainingTool())
    registry.register(MonitorTool())

    # 创建 Agent
    agent = AgentCore(tool_registry=registry)

    return agent


def cmd_execute(args):
    """执行目标"""
    agent = init_agent()
    result = agent.execute_goal(args.goal)

    if result.status == "success":
        print(f"\n✅ 执行成功")
        return 0
    else:
        print(f"\n❌ 执行失败: {result.message}")
        return 1


def cmd_monitor(args):
    """监控系统健康"""
    agent = init_agent()
    health = agent.monitor_system_health()

    print(f"\n📊 系统健康状态: {health.get('status', 'unknown')}")
    print(f"\n当前指标:")
    for metric, value in health.get("metrics", {}).items():
        print(f"  - {metric}: {value}")

    anomalies = health.get("anomalies", [])
    if anomalies:
        print(f"\n⚠️  发现 {len(anomalies)} 个异常:")
        for anomaly in anomalies:
            print(f"  - {anomaly['metric']}: {anomaly['current_value']} (阈值: {anomaly['threshold']})")
            print(f"    {anomaly.get('message', '')}")
    else:
        print(f"\n✅ 所有指标正常")

    return 0


def cmd_status(args):
    """查看 Agent 状态"""
    agent = init_agent()
    status = agent.get_status()

    print(f"\n📊 Agent 状态:")
    print(f"  - 已注册工具: {status['registered_tools']} 个")
    print(f"\n可用工具:")
    for tool in status["tools"]:
        print(f"  - {tool['name']}: {tool['description']}")

    print(f"\n最近决策:")
    for decision in status["recent_decisions"]:
        print(f"  - {decision.get('timestamp', '')}: {decision.get('goal', '')}")

    action_stats = status["action_stats"]
    print(f"\n工具调用统计:")
    print(f"  - 总调用次数: {action_stats.get('total_calls', 0)}")
    print(f"  - 成功率: {action_stats.get('success_rate', 0) * 100:.1f}%")
    print(f"  - 平均耗时: {action_stats.get('avg_duration_ms', 0):.0f}ms")

    return 0


def cmd_tools(args):
    """列出所有工具"""
    agent = init_agent()
    tools = agent.tool_registry.list_tools()

    print(f"\n🔧 已注册工具 ({len(tools)} 个):\n")
    for tool in tools:
        print(f"  {tool['name']}")
        print(f"    {tool['description']}\n")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Agent 系统命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 执行目标
  python -m agent.cli execute "提升多样性"
  python -m agent.cli execute "补充数据"

  # 监控系统健康
  python -m agent.cli monitor

  # 查看 Agent 状态
  python -m agent.cli status

  # 列出所有工具
  python -m agent.cli tools
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # execute 命令
    parser_execute = subparsers.add_parser("execute", help="执行目标")
    parser_execute.add_argument("goal", help="目标描述")
    parser_execute.set_defaults(func=cmd_execute)

    # monitor 命令
    parser_monitor = subparsers.add_parser("monitor", help="监控系统健康")
    parser_monitor.set_defaults(func=cmd_monitor)

    # status 命令
    parser_status = subparsers.add_parser("status", help="查看 Agent 状态")
    parser_status.set_defaults(func=cmd_status)

    # tools 命令
    parser_tools = subparsers.add_parser("tools", help="列出所有工具")
    parser_tools.set_defaults(func=cmd_tools)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
