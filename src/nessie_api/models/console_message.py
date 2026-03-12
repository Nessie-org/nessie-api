from __future__ import annotations
from enum import Enum


class ConsoleMessageType(Enum):
    INFO  = "info"
    OK    = "ok"
    WARN  = "warn"
    ERROR = "error"


class ConsoleMessage:
    """
    One line in console of the workspace.

    Examples::

        ConsoleMessage("Graph loaded successfully.", ConsoleMessageType.OK)
        ConsoleMessage("Missing edge weights.", ConsoleMessageType.WARN)
        ConsoleMessage("3 nodes filtered out.", ConsoleMessageType.INFO)
    """

    def __init__(self, message: str, type: ConsoleMessageType = ConsoleMessageType.INFO) -> None:
        if not isinstance(type, ConsoleMessageType):
            raise TypeError(f"type must be ConsoleMessageType, got {type!r}")
        self.message = message
        self.type    = type

    def to_json(self) -> dict:
        """
        Format::

            {"message": "...", "type": "info"|"ok"|"warn"|"error"}
        """
        return {"message": self.message, "type": self.type.value}

    def __repr__(self) -> str:
        return f"ConsoleMessage({self.message!r}, {self.type})"