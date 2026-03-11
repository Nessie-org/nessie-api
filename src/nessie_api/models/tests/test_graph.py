import unittest
from src.nessie_api.models.graph import Graph, Node, Edge, Attribute, GraphType


class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph = Graph("test_graph", GraphType.DIRECTED)
        self.node1 = Node("n1")
        self.node2 = Node("n2")
        self.edge = Edge("e1", self.node1, self.node2)

    def test_add_node(self):
        self.graph.add_node(self.node1)
        self.assertIn(self.node1, self.graph.nodes)

    def test_remove_node(self):
        self.graph.add_node(self.node1)
        self.graph.remove_node("n1")
        self.assertNotIn(self.node1, self.graph.nodes)

    def test_add_edge(self):
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_edge(self.edge)
        self.assertIn(self.edge, self.graph.edges)

    def test_remove_edge(self):
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_edge(self.edge)
        self.graph.remove_edge("e1")
        self.assertNotIn(self.edge, self.graph.edges)

    def test_serialization(self):
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_edge(self.edge)
        graph_dict = self.graph.to_dict()
        self.assertEqual(graph_dict["name"], "test_graph")
        self.assertEqual(len(graph_dict["nodes"]), 2)
        self.assertEqual(len(graph_dict["edges"]), 1)

    def test_deserialization(self):
        graph_dict = {
            "name": "test_graph",
            "type": "directed",
            "nodes": [
                {"id": "n1", "attributes": {}},
                {"id": "n2", "attributes": {}}
            ],
            "edges": [
                {"id": "e1", "source": "n1", "target": "n2", "attributes": {}}
            ]
        }
        graph = Graph.from_dict(graph_dict)
        self.assertEqual(graph.name, "test_graph")
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 1)

    def test_attributes(self):
        attr = Attribute("weight", 10)
        self.node1.add_attribute(attr)
        self.assertEqual(self.node1.get_attribute("weight").value, 10)
        self.node1.remove_attribute("weight")
        self.assertIsNone(self.node1.get_attribute("weight"))

    def test_neighbors(self):
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_edge(self.edge)
        neighbors = self.graph.out_neighbors(self.node1)
        self.assertIn(self.node2, neighbors)

    def test_node_getitem(self):
        attr = Attribute("color", "red")
        self.node1.add_attribute(attr)
        self.assertEqual(self.node1["color"], "red")

    def test_edge_getitem(self):
        attr = Attribute("weight", 5.5)
        self.edge.add_attribute(attr)
        self.assertEqual(self.edge["weight"], 5.5)

    def test_graph_getitem(self):
        self.graph.add_node(self.node1)
        self.assertEqual(self.graph["n1"], self.node1)


if __name__ == "__main__":
    unittest.main()
