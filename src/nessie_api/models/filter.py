from __future__ import annotations

import json
from enum import Enum
from nessie_api.models import AttributeValue, Attribute


class FilterOperator(Enum):
    EQ = "=="
    NEQ = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="


class FilterExpression:
    """
    <attr_name> <operator> <value>

    Examples:
        FilterExpression("Age", FilterOperator.GT, 30)
        FilterExpression("Name", FilterOperator.EQ, "Alice")
    """

    def __init__(
        self, attr_name: str, operator: FilterOperator, value: AttributeValue
    ) -> None:
        if not isinstance(value, Attribute.SUPPORTED_TYPES):
            raise TypeError(
                f"Filter value must be one of supported types {Attribute.SUPPORTED_TYPES}, got {type(value)}."
            )
        self.attr_name = attr_name
        self.operator = operator
        self.value = value

    @classmethod
    def from_string(cls, expression: str) -> "FilterExpression":
        import re

        pattern = r"^\s*(\w+)\s*(==|!=|<=|>=|<|>)\s*(.+)\s*$"
        match = re.match(pattern, expression)
        if not match:
            raise ValueError(
                f"Illegal filter format: {expression!r}. Expected format: '<attr_name> <operator> <value>'"
            )
        attr_name, op_str, raw_value = (
            match.group(1),
            match.group(2),
            match.group(3).strip(),
        )
        operator = FilterOperator(op_str)
        value = cls._coerce_value(raw_value)
        return cls(attr_name, operator, value)

    @classmethod
    def from_json(cls, json_data: str | dict) -> "FilterExpression":
        """
        JSON format:
        {
            "attr_name": "Age",
            "operator": ">",
            "value": 30
        }
        """
        if isinstance(json_data, str):
            data = json.loads(json_data)
        elif isinstance(json_data, dict):
            data = json_data
        else:
            raise TypeError("Input must be a JSON string or dictionary.")

        if not all(key in data for key in ("attr_name", "operator", "value")):
            raise ValueError(
                "JSON must contain 'attr_name', 'operator', and 'value' keys."
            )

        attr_name = data["attr_name"]
        operator = FilterOperator(data["operator"])
        value = cls._coerce_value(data["value"])

        return cls(attr_name, operator, value)

    def to_string(self) -> str:
        """
        <attr_name> <operator> <value>
        """
        return f"{self.attr_name} {self.operator.value} {self.value}"

    def to_json(self) -> dict:
        """
        Format:
        {
            "attr_name": "Age",
            "operator": ">",
            "value": 30
        }
        """
        return {
            "attr_name": self.attr_name,
            "operator": self.operator.value,
            "value": self.value,
        }

    @staticmethod
    def _coerce_value(raw: str) -> AttributeValue:
        from datetime import date as date_type

        try:
            return int(raw)
        except ValueError:
            pass
        try:
            return float(raw)
        except ValueError:
            pass
        try:
            return date_type.fromisoformat(raw)
        except ValueError:
            pass
        return raw

    def __repr__(self) -> str:
        return (
            f"FilterExpression({self.attr_name!r} {self.operator.value} {self.value!r})"
        )
