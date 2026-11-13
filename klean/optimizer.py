"""Conservative AST optimisation after successful semantic checking.

Only pure scalar expressions are folded. Faulting arithmetic is left intact
so the VM retains its checked error behaviour. Branch removal preserves scopes
and never hides semantic errors, because this pass runs after type checking.
"""
from __future__ import annotations

from dataclasses import dataclass

from .ast import Node
from .semantic import INT_MAX, INT_MIN


@dataclass
class OptimizationStats:
    folded_expressions: int = 0
    simplified_branches: int = 0
    removed_statements: int = 0


class Optimizer:
    def __init__(self):
        self.stats = OptimizationStats()

    def _sequence(self, statements: list[Node]) -> list[Node]:
        result = []
        for index, statement in enumerate(statements):
            rewritten = self._node(statement)
            if rewritten is None:
                self.stats.removed_statements += 1
                continue
            result.append(rewritten)
            if self._returns(rewritten):
                self.stats.removed_statements += len(statements) - index - 1
                break
        return result

    def _returns(self, node: Node) -> bool:
        if node.kind == "Return":
            return True
        if node.kind == "ScopedBlock":
            return self._returns(node.fields["body"])
        if node.kind == "Block":
            body = node.fields["statements"]
            return bool(body) and self._returns(body[-1])
        if node.kind == "If":
            other = node.fields["otherwise"]
            return other is not None and self._returns(node.fields["then"]) and self._returns(other)
        return False

    def _constant(self, node: Node) -> int | bool | None:
        if node.kind == "Integer":
            return int(node.fields["decimal"].lstrip("0") or "0")
        if node.kind == "Boolean":
            return node.fields["value"]
        return None

    def _literal(self, value: int | bool, source: Node) -> Node:
        self.stats.folded_expressions += 1
        if type(value) is bool:
            return Node("Boolean", source.token, {"value": value})
        return Node("Integer", source.token, {"decimal": str(value)})

    def _node(self, node: Node) -> Node | None:
        if node.kind in {"Program", "Block"}:
            key = "items" if node.kind == "Program" else "statements"
            return Node(node.kind, node.token, {key: self._sequence(node.fields[key])})
        fields = {}
        for key, value in node.fields.items():
            if isinstance(value, Node):
                fields[key] = self._node(value)
            elif isinstance(value, list):
                fields[key] = [self._node(v) if isinstance(v, Node) else v for v in value]
            else:
                fields[key] = value
        result = Node(node.kind, node.token, fields)
        if result.kind == "If" and fields["condition"].kind == "Boolean":
            selected = fields["then"] if fields["condition"].fields["value"] else fields["otherwise"]
            self.stats.simplified_branches += 1
            # Keep the original block boundary: flattening would change shadowing.
            return Node("ScopedBlock", result.token, {"body": selected}) if selected else None
        if result.kind == "While" and fields["condition"].kind == "Boolean" and not fields["condition"].fields["value"]:
            self.stats.simplified_branches += 1
            return None
        if result.kind == "Unary":
            value = self._constant(fields["operand"])
            if value is not None:
                folded = -value if fields["operator"] == "-" else not value
                if type(folded) is bool or INT_MIN <= folded <= INT_MAX:
                    return self._literal(folded, result)
        if result.kind == "Binary":
            operator = fields["operator"]
            left = self._constant(fields["left"])
            if operator in {"and", "or"} and type(left) is bool:
                self.stats.folded_expressions += 1
                if (operator == "and" and not left) or (operator == "or" and left):
                    return Node("Boolean", result.token, {"value": left})
                return fields["right"]
            right = self._constant(fields["right"])
            if left is not None and right is not None:
                operations = {
                    "+": lambda: left + right, "-": lambda: left - right,
                    "*": lambda: left * right, "==": lambda: left == right,
                    "!=": lambda: left != right, "<": lambda: left < right,
                    "<=": lambda: left <= right, ">": lambda: left > right,
                    ">=": lambda: left >= right,
                }
                if operator == "/":
                    if right == 0:
                        return result
                    folded = abs(left) // abs(right)
                    if (left < 0) != (right < 0):
                        folded = -folded
                else:
                    folded = operations[operator]()
                if type(folded) is bool or INT_MIN <= folded <= INT_MAX:
                    return self._literal(folded, result)
        return result

    def optimize(self, program: Node) -> Node:
        result = self._node(program)
        assert result is not None
        return result
