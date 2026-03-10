from nessie_api.models import Graph, FilterExpression


class Workspace:
    """
    One workspace = one loaded data source + active filters.
    """

    def __init__(self, source_graph: Graph) -> None:
        self.source_graph = source_graph
        self._filters: list[FilterExpression] = []
        self._undo_stack: list[list[FilterExpression]] = []
        self._redo_stack: list[list[FilterExpression]] = []

    @property
    def active_filters(self) -> list[FilterExpression]:
        return list(self._filters)

    def add_filter(self, operation: FilterExpression) -> None:
        self._undo_stack.append(self._filters.copy())
        self._redo_stack.clear()
        self._filters.append(operation)

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

    def __repr__(self) -> str:
        return f"Workspace(filters={self._filters})"
