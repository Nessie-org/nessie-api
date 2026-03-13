from copy import deepcopy

from nessie_api.models.console_message import ConsoleMessage
from nessie_api.models.filter import FilterExpression
from nessie_api.models.graph import Graph


class Workspace:
    """
    One workspace = one loaded data source + active filters.
    """

    def __init__(self, source_graph: Graph) -> None:
        self.source_graph = source_graph
        self.current_graph = deepcopy(source_graph)
        self.visualiser_name: str | None = None
        self._filters: list[FilterExpression] = []
        self._console_messages: list[ConsoleMessage] = []
        self._undo_stack: list[list[FilterExpression]] = []
        self._redo_stack: list[list[FilterExpression]] = []

    @property
    def active_filters(self) -> list[FilterExpression]:
        return list(self._filters)
    
    @property
    def console_messages(self) -> list[ConsoleMessage]:
        return list(self._console_messages)

    def add_filter(self, operation: FilterExpression) -> None:
        if operation in self._filters:
            return

        self._undo_stack.append(self._filters.copy())
        self._redo_stack.clear()
        self._filters.append(operation)

    def remove_filter(self, operation: FilterExpression) -> None:
        if operation not in self._filters:
            return

        self._undo_stack.append(self._filters.copy())
        self._redo_stack.clear()
        self._filters.remove(operation)

    def add_filters(self, operations: list[FilterExpression]) -> None:
        self._undo_stack.append(self._filters.copy())
        self._redo_stack.clear()
        self._filters.extend(operations)

    def remove_last_filter(self) -> None:
        if self._filters:
            self._undo_stack.append(self._filters.copy())
            self._redo_stack.clear()
            self._filters.pop()

    def clear_filters(self) -> None:
        if self._filters:
            self._undo_stack.append(self._filters.copy())
            self._redo_stack.clear()
            self._filters.clear()

    def undo(self) -> None:
        if self._undo_stack:
            self._redo_stack.append(self._filters.copy())
            self._filters = self._undo_stack.pop()

    def redo(self) -> None:
        if self._redo_stack:
            self._undo_stack.append(self._filters.copy())
            self._filters = self._redo_stack.pop()

    def add_console_message(self, message: ConsoleMessage) -> None:
        self._console_messages.append(message)
    
    def clear_console_messages(self) -> None:
        self._console_messages.clear()

    def __repr__(self) -> str:
        return f"Workspace(filters={self._filters})"
