"""
事件总线

监听系统事件，触发 Agent 自动响应。
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List


class Event:
    """事件"""

    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data


class EventBus:
    """事件总线"""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        订阅事件

        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        取消订阅

        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type in self._listeners:
            self._listeners[event_type].remove(handler)

    def publish(self, event: Event) -> None:
        """
        发布事件

        Args:
            event: 事件对象
        """
        if event.event_type in self._listeners:
            for handler in self._listeners[event.event_type]:
                handler(event)

    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        发送事件（便捷方法）

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        self.publish(Event(event_type, data))
