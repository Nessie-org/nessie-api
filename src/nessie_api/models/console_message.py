from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional


class ConsoleMessageType(Enum):
    INFO  = "info"
    OK    = "ok"
    WARN  = "warn"
    ERROR = "error"
    INPUT = "input"  # clickable prompt — populates the console input field


class ConsoleMessage:
    """
    One console line of the workspace.
    """

    def __init__(
        self,
        message:   str,
        type:      ConsoleMessageType = ConsoleMessageType.INFO,
        timestamp: Optional[datetime] = None,
    ) -> None:
        self.message   = message
        self.type      = type
        self.timestamp = timestamp or datetime.now()

    @classmethod
    def input(cls, label: str) -> "ConsoleMessage":
        return cls(message=label, type=ConsoleMessageType.INPUT)

    @classmethod
    def info(cls, label: str) -> "ConsoleMessage":
        return cls(message=label, type=ConsoleMessageType.INFO)

    @classmethod
    def ok(cls, label: str) -> "ConsoleMessage":
        return cls(message=label, type=ConsoleMessageType.OK)

    @classmethod
    def warn(cls, label: str) -> "ConsoleMessage":
        return cls(message=label, type=ConsoleMessageType.WARN)

    @classmethod
    def error(cls, label: str) -> "ConsoleMessage":
        return cls(message=label, type=ConsoleMessageType.ERROR)

    def to_json(self) -> dict:
        return {
            "message":   self.message,
            "type":      self.type.value,
            "timestamp": self.timestamp.strftime("%H:%M:%S"),
        }

    def __repr__(self) -> str:
        return f"ConsoleMessage({self.message!r}, {self.type})"