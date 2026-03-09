from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional, Union

AttributeValue = Union[int, float, str, date]


class GraphType(Enum):
    DIRECTED = "directed"
    UNDIRECTED = "undirected"


class Attribute:

    SUPPORTED_TYPES = (int, float, str, date)

    def __init__(self, name: str, value: AttributeValue) -> None:
        if not isinstance(value, self.SUPPORTED_TYPES):
            raise TypeError(
                f"Attribute value must be one of {self.SUPPORTED_TYPES}, got {type(value)}."
            )
        self.name = name
        self.value = value

    @property
    def value_type(self) -> type:
        return type(self.value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        if not isinstance(new, self.SUPPORTED_TYPES):
            raise TypeError(
                f"Attribute value must be one of {self.SUPPORTED_TYPES}, got {type(new)}."
            )
        self._value = new

    def __repr__(self) -> str:
        return f"Attribute({self.name!r}, {self.value!r})"


class Node:

    def __init__(self, node_id: str, attributes: Optional[dict[str, Attribute]] = None) -> None:
        self.id = node_id
        self.attributes: dict[str, Attribute] = attributes or {}

    def add_attribute(self, attribute: Attribute) -> None:
        self.attributes[attribute.name] = attribute

    def get_attribute(self, name: str) -> Optional[Attribute]:
        return self.attributes.get(name)

    def remove_attribute(self, name: str) -> None:
        self.attributes.pop(name, None)

    def __getitem__(self, name: str) -> AttributeValue:
        if name not in self.attributes:
            raise KeyError(f"Attribute {name!r} not found.")
        return self.attributes[name].value

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False
        return self.id == other.id

    def __repr__(self) -> str:
        return f"Node(id={self.id!r}, attributes={list(self.attributes.keys())})"


class Edge:

    def __init__(
        self,
        edge_id: str,
        source: Node,
        target: Node,
        attributes: Optional[dict[str, Attribute]] = None,
    ) -> None:
        self.id = edge_id
        self.source = source
        self.target = target
        self.attributes: dict[str, Attribute] = attributes or {}

    def add_attribute(self, attribute: Attribute) -> None:
        self.attributes[attribute.name] = attribute

    def get_attribute(self, name: str) -> Optional[Attribute]:
        return self.attributes.get(name)

    def remove_attribute(self, name: str) -> None:
        self.attributes.pop(name, None)

    def connects(self, node_a: Node, node_b: Node) -> bool:
        return self.source is node_a and self.target is node_b

    def __getitem__(self, name: str) -> AttributeValue:
        if name not in self.attributes:
            raise KeyError(f"Attribute {name!r} not found.")
        return self.attributes[name].value

    def __repr__(self) -> str:
        return f"Edge({self.source.id!r} -> {self.target.id!r})"


class Graph:

    def __init__(self, graph_type: GraphType = GraphType.DIRECTED) -> None:
        self.graph_type = graph_type

        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, Edge] = {}

        self._adj_out: dict[str, set[str]] = {}
        self._adj_in: dict[str, set[str]] = {}

    # ── Nodes ──────────────────────────────

    def add_node(self, node: Node) -> None:
        if node.id in self._nodes:
            raise ValueError(f"Node with id {node.id!r} already exists.")

        self._nodes[node.id] = node
        self._adj_out[node.id] = set()
        self._adj_in[node.id] = set()

    def get_node(self, node_id: str) -> Optional[Node]:
        return self._nodes.get(node_id)

    def remove_node(self, node_id: str) -> None:
        if node_id not in self._nodes:
            raise KeyError(f"Node with id {node_id!r} doesn't exist.")

        if self._adj_out[node_id] or self._adj_in[node_id]:
            raise ValueError("Cannot remove node with edges.")

        del self._nodes[node_id]
        del self._adj_out[node_id]
        del self._adj_in[node_id]

    @property
    def nodes(self) -> list[Node]:
        return list(self._nodes.values())

    def __getitem__(self, node_id: str) -> Node:
        if node_id not in self._nodes:
            raise KeyError(f"Node with id {node_id!r} not found.")
        return self._nodes[node_id]

    # ── Edges ────────────────────────────────

    def add_edge(self, edge: Edge) -> None:
        if edge.id in self._edges:
            raise ValueError(f"Edge with id {edge.id!r} already exists.")

        if edge.source.id not in self._nodes or edge.target.id not in self._nodes:
            raise ValueError("Source and target nodes must exist.")

        self._edges[edge.id] = edge

        self._adj_out[edge.source.id].add(edge.target.id)
        self._adj_in[edge.target.id].add(edge.source.id)

        if self.graph_type == GraphType.UNDIRECTED:
            self._adj_out[edge.target.id].add(edge.source.id)
            self._adj_in[edge.source.id].add(edge.target.id)

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        return self._edges.get(edge_id)

    def remove_edge(self, edge_id: str) -> None:

        if edge_id not in self._edges:
            raise KeyError(f"Edge with id {edge_id!r} doesn't exist.")

        edge = self._edges[edge_id]

        self._adj_out[edge.source.id].discard(edge.target.id)
        self._adj_in[edge.target.id].discard(edge.source.id)

        if self.graph_type == GraphType.UNDIRECTED:
            self._adj_out[edge.target.id].discard(edge.source.id)
            self._adj_in[edge.source.id].discard(edge.target.id)

        del self._edges[edge_id]

    @property
    def edges(self) -> list[Edge]:
        return list(self._edges.values())

    # ── Neighbors ───────────────────

    def out_neighbors(self, node: Node) -> list[Node]:
        if node.id not in self._nodes:
            raise KeyError(f"Node {node.id!r} is not in the graph.")

        return [self._nodes[nid] for nid in self._adj_out[node.id]]

    def in_neighbors(self, node: Node) -> list[Node]:
        if node.id not in self._nodes:
            raise KeyError(f"Node {node.id!r} is not in the graph.")

        return [self._nodes[nid] for nid in self._adj_in[node.id]]

    def neighbors(self, node: Node) -> list[Node]:
        if node.id not in self._nodes:
            raise KeyError(f"Node {node.id!r} is not in the graph.")

        ids = self._adj_out[node.id] | self._adj_in[node.id]
        return [self._nodes[nid] for nid in ids]

    # ── Date helpers ───────────────────

    @staticmethod
    def _serialize(value):
        if isinstance(value, date):
            return value.isoformat()
        return value

    @staticmethod
    def _deserialize(value):
        try:
            return date.fromisoformat(value)
        except TypeError | ValueError:
            return value

    # ── Format ───────────────────

    def to_dict(self) -> dict:
        return {
            "type": self.graph_type.value,
            "nodes": [
                {
                    "id": n.id,
                    "attributes": {k: self._serialize(v.value) for k, v in n.attributes.items()}
                }
                for n in self._nodes.values()
            ],
            "edges": [
                {
                    "id": e.id,
                    "source": e.source.id,
                    "target": e.target.id,
                    "attributes": {k: self._serialize(v.value) for k, v in e.attributes.items()}
                }
                for e in self._edges.values()
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Graph":

        graph = cls(GraphType(data["type"]))

        node_map: dict[str, Node] = {}

        for n in data["nodes"]:
            node = Node(n["id"])
            for k, v in n["attributes"].items():
                node.add_attribute(Attribute(k, cls._deserialize(v)))
            graph.add_node(node)
            node_map[node.id] = node

        for e in data["edges"]:
            edge = Edge(
                e["id"],
                node_map[e["source"]],
                node_map[e["target"]],
            )

            for k, v in e["attributes"].items():
                edge.add_attribute(Attribute(k, cls._deserialize(v)))

            graph.add_edge(edge)

        return graph

    def __repr__(self) -> str:
        return (
            f"Graph(type={self.graph_type.value}, "
            f"nodes={len(self._nodes)}, edges={len(self._edges)})"
        )
