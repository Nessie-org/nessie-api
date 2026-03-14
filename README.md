# nessie-api

**nessie-api** is a Python library that provides the shared models and contracts for the Nessie platform — a graph-based data lakehouse visualization tool. It defines the core data structures (graphs, filters, workspaces), a plugin system for extending functionality, and a `Context` protocol that plugins use to interact with the host environment.

> **Status:** Alpha (`v0.1.0`) — API is subject to change.  
> **License:** Apache 2.0  
> **Python:** 3.9+

---

## Table of Contents

- [Installation](#installation)
- [Architecture Overview](#architecture-overview)
- [Package Structure](#package-structure)
- [Core Models](#core-models)
  - [Graph](#graph)
  - [Node](#node)
  - [Edge](#edge)
  - [Attribute](#attribute)
  - [FilterExpression](#filterexpression)
  - [Workspace](#workspace)
  - [ConsoleMessage](#consolemessage)
- [Plugin System](#plugin-system)
  - [Defining a Plugin](#defining-a-plugin)
  - [Plugin Lifecycle](#plugin-lifecycle)
  - [Registering via Entry Points](#registering-via-entry-points)
- [Context Protocol](#context-protocol)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Contributing](#contributing)

---

## Installation

```bash
pip install nessie-api
```

For development (includes testing, linting, and type-checking tools):

```bash
pip install "nessie-api[dev]"
```

**Requirements:** Python ≥ 3.9. The package has **no runtime dependencies**.

---

## Architecture Overview

```
nessie-api
├── Models        Core data structures (Graph, Workspace, Filter, ConsoleMessage)
├── Plugin        Decorator-based plugin registration + Action dispatch
└── Protocols     Context interface — the bridge between plugins and the host app
```

The library is intentionally dependency-free. It defines the *contracts* (models and protocols) that both the Nessie host application and third-party plugins depend on, without implementing any UI or storage logic itself.

---

## Package Structure

```
src/
├── main.py                         Entry point / demo runner
├── demo_plugin/
│   └── __init__.py                 Example plugin implementation
└── nessie_api/
    ├── __init__.py
    ├── models/
    │   ├── graph.py                Graph, Node, Edge, Attribute
    │   ├── filter.py               FilterExpression, FilterOperator
    │   ├── workspace.py            Workspace (filter state + undo/redo)
    │   ├── plugin.py               Plugin, Action, @plugin decorator
    │   ├── console_message.py      ConsoleMessage, ConsoleMessageType
    │   └── tests/
    │       ├── test_graph.py
    │       ├── test_filter.py
    │       └── test_workspace.py
    └── protocols/
        └── context.py              Context protocol
```

---

## Core Models

All models are exported from `nessie_api.models`:

```python
from nessie_api.models import (
    Graph, Node, Edge, Attribute, AttributeValue, GraphType,
    FilterOperator, FilterExpression,
    Workspace,
    Plugin, Action, plugin, NoAvailablePluginError, SetupRequirementType,
    ConsoleMessage, ConsoleMessageType,
)
```

---

### Graph

`Graph` is the central data structure. It supports both directed and undirected graphs and maintains internal adjacency lists for fast neighbor lookups.

```python
from nessie_api.models import Graph, GraphType

g = Graph("my_graph", GraphType.DIRECTED)   # default is DIRECTED
g = Graph("my_graph", GraphType.UNDIRECTED)
```

#### Adding and Removing Nodes

```python
from nessie_api.models import Node

node_a = Node("a")
node_b = Node("b")

g.add_node(node_a)
g.add_node(node_b)

g.get_node("a")        # → Node or None
g["a"]                 # → Node (raises KeyError if missing)
g.nodes                # → list[Node]

g.remove_node("a")     # raises ValueError if node still has edges
```

#### Adding and Removing Edges

```python
from nessie_api.models import Edge

edge = Edge("e1", node_a, node_b)
g.add_edge(edge)

g.get_edge("e1")       # → Edge or None
g.edges                # → list[Edge]

g.remove_edge("e1")
```

#### Traversal

```python
g.out_neighbors(node_a)   # → list[Node]  (nodes reachable from node_a)
g.in_neighbors(node_b)    # → list[Node]  (nodes pointing to node_b)
g.neighbors(node_a)       # → list[Node]  (union of in + out)
```

#### Serialization

```python
data = g.to_dict()         # → dict (JSON-compatible)
g2   = Graph.from_dict(data)
```

The dict format is:

```json
{
  "name": "my_graph",
  "type": "directed",
  "nodes": [
    { "id": "a", "attributes": { "weight": 1 } }
  ],
  "edges": [
    { "id": "e1", "source": "a", "target": "b", "attributes": {} }
  ]
}
```

`date` attribute values are automatically serialized to/from ISO 8601 strings.

---

### Node

```python
from nessie_api.models import Node, Attribute

node = Node("n1")

# Add / get / remove attributes
node.add_attribute(Attribute("color", "red"))
node.get_attribute("color")     # → Attribute or None
node["color"]                   # → "red"  (shorthand, raises KeyError if missing)
node.remove_attribute("color")
```

Nodes are hashed and compared by their `id`.

---

### Edge

```python
from nessie_api.models import Edge, Node

edge = Edge("e1", source_node, target_node)

edge.source          # → Node
edge.target          # → Node
edge["weight"]       # → AttributeValue  (shorthand attribute access)
edge.connects(a, b)  # → bool
```

Edges support the same `add_attribute` / `get_attribute` / `remove_attribute` interface as `Node`.

---

### Attribute

Attributes attach typed key-value metadata to nodes and edges. Supported value types (`AttributeValue`) are: `int`, `float`, `str`, and `datetime.date`.

```python
from nessie_api.models import Attribute
from datetime import date

Attribute("score",    95)
Attribute("label",    "Alice")
Attribute("ratio",    3.14)
Attribute("created",  date(2024, 1, 1))

attr = Attribute("score", 95)
attr.name        # → "score"
attr.value       # → 95
attr.value_type  # → <class 'int'>

attr.value = 100  # validated on assignment — raises TypeError for wrong types
```

---

### FilterExpression

A `FilterExpression` represents a predicate of the form `<attr_name> <operator> <value>` that can be applied to filter nodes or edges in a workspace.

**Operators** (`FilterOperator`): `EQ (==)`, `NEQ (!=)`, `LT (<)`, `LTE (<=)`, `GT (>)`, `GTE (>=)`.

#### Construction

```python
from nessie_api.models import FilterExpression, FilterOperator

# Directly
expr = FilterExpression("Age", FilterOperator.GT, 30)

# From a string
expr = FilterExpression.from_string("Age > 30")
expr = FilterExpression.from_string("Name == Alice")

# From JSON (string or dict)
expr = FilterExpression.from_json('{"attr_name": "Age", "operator": ">", "value": 30}')
expr = FilterExpression.from_json({"attr_name": "Age", "operator": ">", "value": 30})
```

#### Serialization

```python
expr.to_string()  # → "Age > 30"
expr.to_json()    # → {"attr_name": "Age", "operator": ">", "value": 30}
```

Value coercion in `from_string` and `from_json` automatically converts raw strings to `int`, `float`, `date`, or `str` in that order of precedence.

---

### Workspace

A `Workspace` pairs a source graph with a mutable list of active `FilterExpression` objects and maintains a full undo/redo history. It is also the home for workspace-level console messages.

```python
from nessie_api.models import Workspace, Graph

ws = Workspace(source_graph=Graph("g"))
```

`source_graph` is stored as the original and `current_graph` is a deep copy that reflects filtered state.

#### Managing Filters

```python
ws.add_filter(expr)           # no-op if expr already active
ws.remove_filter(expr)        # no-op if expr not present
ws.add_filters([expr1, expr2])
ws.remove_last_filter()
ws.clear_filters()

ws.active_filters             # → list[FilterExpression] (copy)
```

#### Undo / Redo

Every mutating filter operation pushes the previous filter list to the undo stack.

```python
ws.undo()   # restore previous filter state
ws.redo()   # re-apply undone state
```

#### Console Messages

```python
from nessie_api.models import ConsoleMessage

ws.add_console_message(ConsoleMessage.info("Graph loaded."))
ws.console_messages      # → list[ConsoleMessage]
ws.clear_console_messages()
```

---

### ConsoleMessage

Represents a single log line in the workspace console panel.

**Types** (`ConsoleMessageType`): `INFO`, `OK`, `WARN`, `ERROR`, `INPUT` (clickable prompt).

```python
from nessie_api.models import ConsoleMessage

ConsoleMessage.info("Ready.")
ConsoleMessage.ok("Filters applied.")
ConsoleMessage.warn("Large graph — rendering may be slow.")
ConsoleMessage.error("Failed to load file.")
ConsoleMessage.input("Click to run default query")   # populates console input

msg.to_json()
# → {"message": "Ready.", "type": "info", "timestamp": "14:03:22"}
```

---

## Plugin System

Nessie is extended through **plugins** — Python packages that register themselves via [entry points](https://packaging.python.org/en/latest/specifications/entry-points/) under the `nessie_plugins` group.

### Defining a Plugin

Use the `@plugin` decorator on a factory function that returns a configuration dict:

```python
from nessie_api.models import plugin, Action
from nessie_api.protocols import Context

@plugin(name="my_plugin", verbose=True)
def my_plugin_factory():

    def load_graph(action: Action, context: Context):
        graph = ...  # build a Graph from action.payload
        context.add_workspace(graph)

    def apply_filter(action: Action, context: Context):
        expr = FilterExpression.from_json(action.payload)
        idx  = context.get_active_workspace_index()
        context.add_filter_at(idx, expr)

    return {
        "handlers": {
            "load_graph":   load_graph,
            "apply_filter": apply_filter,
        },
        "requires":       [],        # names of other plugins this depends on
        "setup_requires": {},        # see SetupRequirementType
    }
```

The decorator wraps the factory so that calling `my_plugin_factory()` returns a fully constructed `Plugin` instance.

### Plugin Lifecycle

```python
plugin_instance = my_plugin_factory()

plugin_instance.activate()                              # called when plugin is loaded
plugin_instance.provided_actions                        # → ["load_graph", "apply_filter"]

action = Action(name="load_graph", payload={"path": "/data/graph.json"})
plugin_instance.handle(action, context)                 # dispatches to the right handler

plugin_instance.deactivate()                            # called on unload
```

`handle` is a no-op if no handler is registered for `action.name`.

### Setup Requirements

Plugins that need user-provided configuration declare `setup_requires`:

```python
from nessie_api.models import SetupRequirementType

return {
    "handlers": { ... },
    "setup_requires": {
        "api_key":  SetupRequirementType.STRING,
        "port":     SetupRequirementType.NUMBER,
        "debug":    SetupRequirementType.BOOLEAN,
        "cert":     SetupRequirementType.FILE,
    },
}
```

`SetupRequirementType` values: `STRING`, `NUMBER`, `BOOLEAN`, `FILE`.

### Registering via Entry Points

In your plugin package's `pyproject.toml`:

```toml
[project.entry-points."nessie_plugins"]
my_plugin = "my_package:my_plugin_factory"
```

The host application discovers plugins at startup:

```python
from importlib.metadata import entry_points

plugins = entry_points(group="nessie_plugins")
for entry in plugins:
    instance = entry.load()()   # call factory → Plugin
    instance.activate()
```

---

## Context Protocol

The `Context` protocol (defined in `nessie_api.protocols.context`) is the interface between a plugin and the host application. Plugins receive a `Context` object as the second argument to every action handler.

Implement `Context` in the host application by satisfying the protocol structurally (no explicit inheritance required).

### Workspace Management

| Method | Description |
|--------|-------------|
| `get_workspace_count() → int` | Total number of open workspaces (≥ 1). |
| `get_active_workspace_index() → int \| None` | Index of the currently active workspace. |
| `set_active_workspace_index(index)` | Switch the active workspace. |
| `add_workspace(graph: Graph)` | Open a new workspace with the given graph. |
| `close_workspace_at(index)` | Close the workspace at `index`. |

### Graph Access

| Method | Description |
|--------|-------------|
| `get_graph_at(index) → Graph` | Filtered graph at `index`. |
| `get_full_graph_at(index) → Graph` | Unfiltered source graph at `index`. |
| `set_graph_at(index, graph)` | Replace the filtered graph. |
| `set_full_graph_at(index, graph)` | Replace the source graph. |

### Visualisation

| Method | Description |
|--------|-------------|
| `get_visualised_graph_at(index) → str` | HTML string produced by the active visualiser plugin. |
| `get_visualiser_name_at(index) → str` | Name of the active visualiser plugin. |
| `set_visualiser_at(index, name)` | Change the visualiser plugin for a workspace. |

### Filters

| Method | Description |
|--------|-------------|
| `get_active_filters_at(index) → list` | Currently active `FilterExpression` objects. |
| `add_filter_at(index, expr)` | Add a filter to the workspace. |
| `remove_filter_at(index, expr)` | Remove a specific filter. |
| `clear_filters_at(index)` | Remove all filters. |

### Search

| Method | Description |
|--------|-------------|
| `get_search_at(index) → str` | Current search query string. |
| `set_search_at(index, query)` | Set the search query. |

### Console

| Method | Description |
|--------|-------------|
| `get_console_messages_at(index) → list` | Console messages for the workspace. |
| `add_console_message_at(index, msg)` | Append a `ConsoleMessage`. |
| `clear_console_messages_at(index)` | Clear all messages. |

### Action Dispatch

| Method | Description |
|--------|-------------|
| `perform_action(action, plugin_name=None)` | Dispatch an `Action`. If `plugin_name` is given, only that plugin handles it; otherwise any capable plugin may handle it. |

---

## Development Setup

```bash
git clone https://github.com/Nessie-org/nessie-api.git
cd nessie-api
pip install -e ".[dev]"
```

The dev extras include `pytest`, `pytest-cov`, `black`, `ruff`, and `mypy`.

### Code Style

```bash
black src/          # format
ruff check src/     # lint
mypy src/           # type-check (strict mode)
```

---

## Running Tests

```bash
pytest
```

Coverage is reported automatically (configured to cover `src/nessie_api`). Tests live in `src/nessie_api/models/tests/` and cover `Graph`, `FilterExpression`, and `Workspace`.

To run the demo entry point and verify plugin discovery:

```bash
python -m src.main
```

---

## Contributing

1. Fork the repository and create a feature branch.
2. Ensure `black`, `ruff`, and `mypy` all pass with no errors.
3. Add or update tests for any changed behaviour.
4. Open a pull request against `main`.

Issues and feature requests: https://github.com/Nessie-org/nessie-api/issues
