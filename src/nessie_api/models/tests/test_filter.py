import unittest
from src.nessie_api.models.filter import FilterExpression, FilterOperator


class TestFilterExpression(unittest.TestCase):
    def test_from_string(self):
        expr = "Age > 30"
        filter_expr = FilterExpression.from_string(expr)
        self.assertEqual(filter_expr.attr_name, "Age")
        self.assertEqual(filter_expr.operator, FilterOperator.GT)
        self.assertEqual(filter_expr.value, 30)

    def test_from_string_invalid_format(self):
        expr = "InvalidFormat"
        with self.assertRaises(ValueError):
            FilterExpression.from_string(expr)

    def test_from_json_with_string(self):
        json_data = '{"attr_name": "Age", "operator": ">", "value": 30}'
        filter_expr = FilterExpression.from_json(json_data)
        self.assertEqual(filter_expr.attr_name, "Age")
        self.assertEqual(filter_expr.operator, FilterOperator.GT)
        self.assertEqual(filter_expr.value, 30)

    def test_from_json_with_dict(self):
        json_data = {"attr_name": "Age", "operator": ">", "value": 30}
        filter_expr = FilterExpression.from_json(json_data)
        self.assertEqual(filter_expr.attr_name, "Age")
        self.assertEqual(filter_expr.operator, FilterOperator.GT)
        self.assertEqual(filter_expr.value, 30)

    def test_from_json_invalid_format(self):
        json_data = '{"attr_name": "Age", "operator": ">"}'
        with self.assertRaises(ValueError):
            FilterExpression.from_json(json_data)

    def test_to_string(self):
        filter_expr = FilterExpression("Age", FilterOperator.GT, 30)
        self.assertEqual(filter_expr.to_string(), "Age > 30")

    def test_to_json(self):
        filter_expr = FilterExpression("Age", FilterOperator.GT, 30)
        expected_json = {
            "attr_name": "Age",
            "operator": ">",
            "value": 30,
        }
        self.assertEqual(filter_expr.to_json(), expected_json)


if __name__ == "__main__":
    unittest.main()