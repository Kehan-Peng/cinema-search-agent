"""
Agent 系统测试脚本

测试 Agent 系统的核心功能。
"""

from __future__ import annotations

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


def test_tool_registry():
    """测试工具注册中心"""
    print("\n" + "=" * 60)
    print("测试 1: 工具注册中心")
    print("=" * 60)

    registry = ToolRegistry()

    # 注册工具
    registry.register(CrawlerTool())
    registry.register(EvaluationTool())
    registry.register(TrainingTool())
    registry.register(MonitorTool())

    # 列出工具
    tools = registry.list_tools()
    print(f"\n✅ 成功注册 {len(tools)} 个工具:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")

    assert len(tools) == 4, "应该注册 4 个工具"
    print("\n✅ 工具注册中心测试通过")


def test_evaluation_tool():
    """测试评估工具"""
    print("\n" + "=" * 60)
    print("测试 2: 评估工具")
    print("=" * 60)

    registry = ToolRegistry()
    registry.register(EvaluationTool())

    # 调用评估工具
    result = registry.call_tool("evaluation_tool", top_k=5)

    if result.status.value == "success":
        print(f"\n✅ 评估工具执行成功")
        print(f"  - 评估用户数: {result.output.get('sample_users', 0)}")
        print(f"  - 评估算法数: {len(result.output.get('metrics', []))}")
        print(f"  - 耗时: {result.duration_ms}ms")
    else:
        print(f"\n⚠️  评估工具执行失败: {result.error}")

    print("\n✅ 评估工具测试完成")


def test_monitor_tool():
    """测试监控工具"""
    print("\n" + "=" * 60)
    print("测试 3: 监控工具")
    print("=" * 60)

    registry = ToolRegistry()
    registry.register(MonitorTool())

    # 调用监控工具
    result = registry.call_tool(
        "monitor_tool",
        metrics=["diversity", "coverage", "precision@5"],
        thresholds={"diversity": 0.4, "coverage": 0.3, "precision@5": 0.2},
    )

    if result.status.value == "success":
        print(f"\n✅ 监控工具执行成功")
        print(f"  - 系统状态: {result.output.get('status', 'unknown')}")
        print(f"  - 当前指标: {result.output.get('metrics', {})}")
        print(f"  - 异常数量: {len(result.output.get('anomalies', []))}")
        print(f"  - 耗时: {result.duration_ms}ms")
    else:
        print(f"\n⚠️  监控工具执行失败: {result.error}")

    print("\n✅ 监控工具测试完成")


def test_agent_core():
    """测试 Agent 核心"""
    print("\n" + "=" * 60)
    print("测试 4: Agent 核心")
    print("=" * 60)

    # 创建工具注册中心
    registry = ToolRegistry()
    registry.register(EvaluationTool())
    registry.register(MonitorTool())

    # 创建 Agent
    agent = AgentCore(tool_registry=registry)

    # 测试系统健康检查
    print("\n执行目标: 系统健康检查")
    result = agent.execute_goal("系统健康检查")

    if result.status == "success":
        print(f"\n✅ Agent 执行成功")
        print(f"  - 执行任务数: {len(result.actions)}")
        print(f"  - 结果: {result.message}")
    else:
        print(f"\n⚠️  Agent 执行失败: {result.message}")

    print("\n✅ Agent 核心测试完成")


def test_agent_status():
    """测试 Agent 状态查询"""
    print("\n" + "=" * 60)
    print("测试 5: Agent 状态查询")
    print("=" * 60)

    # 创建工具注册中心
    registry = ToolRegistry()
    registry.register(CrawlerTool())
    registry.register(EvaluationTool())
    registry.register(TrainingTool())
    registry.register(MonitorTool())

    # 创建 Agent
    agent = AgentCore(tool_registry=registry)

    # 获取状态
    status = agent.get_status()

    print(f"\n✅ Agent 状态:")
    print(f"  - 已注册工具: {status['registered_tools']} 个")
    print(f"  - 最近决策: {len(status['recent_decisions'])} 条")
    print(f"  - 工具调用统计: {status['action_stats']}")

    print("\n✅ Agent 状态查询测试完成")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Agent 系统测试")
    print("=" * 60)

    try:
        test_tool_registry()
        test_evaluation_tool()
        test_monitor_tool()
        test_agent_core()
        test_agent_status()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
