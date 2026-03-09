import unittest
from src.nessie_api.models import Graph, FilterExpression
from src.nessie_api.models.workspace import Workspace


class TestWorkspaceUndoRedo(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.workspace = Workspace(self.graph)

    def test_add_filter_and_undo(self):
        filter1 = FilterExpression.from_string("Age > 30")
        filter2 = FilterExpression.from_string("Name == 'Alice'")

        self.workspace.add_filter(filter1)
        self.workspace.add_filter(filter2)

        self.assertEqual(self.workspace.active_filters, [filter1, filter2])

        self.workspace.undo()
        self.assertEqual(self.workspace.active_filters, [filter1])

        self.workspace.undo()
        self.assertEqual(self.workspace.active_filters, [])

    def test_undo_and_redo(self):
        filter1 = FilterExpression.from_string("Age > 30")
        filter2 = FilterExpression.from_string("Name == 'Alice'")

        self.workspace.add_filter(filter1)
        self.workspace.add_filter(filter2)

        self.workspace.undo()
        self.workspace.redo()

        self.assertEqual(self.workspace.active_filters, [filter1, filter2])

    def test_clear_filters(self):
        filter1 = FilterExpression.from_string("Age > 30")
        self.workspace.add_filter(filter1)

        self.workspace.clear_filters()
        self.assertEqual(self.workspace.active_filters, [])

        self.workspace.undo()
        self.assertEqual(self.workspace.active_filters, [filter1])

    def test_remove_last_filter(self):
        filter1 = FilterExpression.from_string("Age > 30")
        filter2 = FilterExpression.from_string("Name == 'Alice'")

        self.workspace.add_filter(filter1)
        self.workspace.add_filter(filter2)

        self.workspace.remove_last_filter()
        self.assertEqual(self.workspace.active_filters, [filter1])

        self.workspace.undo()
        self.assertEqual(self.workspace.active_filters, [filter1, filter2])


if __name__ == "__main__":
    unittest.main()
