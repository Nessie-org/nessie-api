from typing import Any, Protocol
from nessie_api.models import ConsoleMessage, Graph, Action, FilterExpression

class Context(Protocol):
    """
    Context protocol that provides methods availabe to the plugin to change 
    the shared enviorement.
    """

    ################## WORKSPACE ##################

    def get_workspace_count(self) -> int:
        """Total number of workspaces. Must be ≥ 1."""
        ...

    def get_active_workspace_index(self) -> int:
        """
        Index of a currently open (and active) workspace.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    def set_active_workspace_index(self, index: int) -> None:
        """
        Sets the active workspace to the one at *index*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    def add_workspace(self, graph: "Graph") -> None:
        """
        Adds a new workspace with the given graph.
        """
        ...

    def close_workspace_at(self, index: int) -> None:
        """
        Closes the workspace at *index*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...


    ################## GRAPHS ##################

    def get_graph_at(self, index: int) -> "Graph":
        """
        Returns the current graph displayed at *index*.
        This graph already has all the filters applied
        """
        ...

    def get_full_graph_at(self, index: int) -> "Graph":
        """
        Returns the full graph at *index* without any filters applied.
        """
        ...

    def set_graph_at(self, index: int, graph: "Graph") -> None:
        """
        Sets the graph at *index* to *graph*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    def set_full_graph_at(self, index: int, graph: "Graph") -> None:
        """
        Sets the full graph at *index* to *graph*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    ################## VISUALISATION ##################

    def get_visualised_graph_at(self, index: int) -> str:
        """
        Returns the visualised graph at *index* as an HTML string.
        This is the result of the visualisation plugin that is currently active for the graph at *index*.
        """
        ...

    def get_visualiser_name_at(self, active_index: int) -> str:
        """
        Returns the name of the visualiser plugin that is currently active for the graph at *index*.
        """
        ...

    def set_visualiser_at(self, index: int, visualiser_name: str) -> None:
        """
        Sets the visualiser plugin for the graph at *index* to *visualiser_name*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    ################## FILTERS ##################

    def get_active_filters_at(self, index: int) -> list:
        """
        Vraća listu FilterExpression objekata koji su trenutno aktivni za graf
        na poziciji *index*. Svaki element mora imati metod .to_json() koji
        vraća {"attr_name": str, "operator": str, "value": any}.
        Default: prazna lista.
        """
        return []
    
    def add_filter_at(self, index: int, filter_expression: "FilterExpression") -> None:
        """
        Adds a new filter to the graph at *index*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    def remove_filter_at(self, index: int, filter_expression: "FilterExpression") -> None:
        """
        Removes a filter from the graph at *index*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    def clear_filters_at(self, index: int) -> None:
        """
        Clears all filters from the graph at *index*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    ################ CONSOLE ##################

    def get_console_messages_at(self, index: int) -> list:
        """
        Vraća listu ConsoleMessage objekata koji će biti prikazani u konzoli
        workspace-a pri prvom učitavanju. Svaki element mora imati metod
        .to_json() koji vraća {"message": str, "type": "info"|"ok"|"warn"|"error"}.
        Default: prazna lista.
        """
        return []
    
    def add_console_message_at(self, index: int, message: "ConsoleMessage") -> None:
        """
        Adds a new console message to the workspace at *index*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    def clear_console_messages_at(self, index: int) -> None:
        """
        Clears all console messages from the workspace at *index*.
        Must be within ``[0, get_workspace_count())``.
        """
        ...

    ################## ACTIONS ##################

    def perform_action(self, action: "Action") -> Any:
        """
        Performs the given action in the shared environment.
        """
        ...