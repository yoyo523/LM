"""Static semantic analysis for Klean.

The analyser resolves names with nested lexical scopes, checks function calls,
and enforces Klean's two primitive types (``int`` and ``bool``).
"""
from __future__ import annotations

from dataclasses import dataclass

from .ast import Diagnostic, Node


INT_MIN = -(2**31)
INT_MAX = 2**31 - 1
BUILTINS = {"input", "array", "len", "collect"}


@dataclass(frozen=True)
class FunctionType:
    parameters: tuple[str, ...]
    result: str
    type_parameters: tuple[str, ...] = ()


@dataclass(frozen=True)
class VariableType:
    type_name: str
    constant: bool = False


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []
        self.functions: dict[str, FunctionType] = {}
        self.scopes: list[dict[str, VariableType]] = []
        self.current_return_type: str | None = None
        self.type_parameters: set[str] = set()

    def error(self, node: Node, message: str) -> None:
        token = node.fields.get("target_token", node.fields.get("name_token", node.token))
        self.diagnostics.append(
            Diagnostic(token.line, token.column, message)
        )

    def analyse(self, program: Node) -> list[Diagnostic]:
        self.diagnostics = []
        self.functions = {}
        self.scopes = [{}]
        self.current_return_type = None
        self.type_parameters = set()

        items = program.fields["items"]
        for item in items:
            if item.kind == "Function":
                self._declare_function(item)

        for item in items:
            if item.kind == "Function":
                self._function(item)
            else:
                self._statement(item)
        return self.diagnostics

    def _declare_function(self, node: Node) -> None:
        name = node.fields["name"]
        if name in BUILTINS:
            self.error(node, f"Function name {name!r} is reserved for a builtin")
            return
        if name in self.functions:
            self.error(node, f"Function {name!r} is already declared")
            return
        parameters = tuple(p.fields["type"] for p in node.fields["parameters"])
        type_parameters = tuple(node.fields.get("type_parameters", []))
        if len(set(type_parameters)) != len(type_parameters):
            self.error(node, "Duplicate generic type parameter")
        for generic in type_parameters:
            if not any(t in {generic, generic + "[]"} for t in parameters):
                self.error(node, f"Generic type {generic!r} must occur in a parameter type")
        self.functions[name] = FunctionType(parameters, node.fields["return_type"], type_parameters)

    def _push_scope(self) -> None:
        self.scopes.append({})

    def _pop_scope(self) -> None:
        self.scopes.pop()

    def _declare_variable(self, node: Node, name: str, type_name: str,
                          constant: bool = False) -> None:
        scope = self.scopes[-1]
        if name in scope:
            self.error(node, f"Variable {name!r} is already declared in this scope")
        else:
            scope[name] = VariableType(type_name, constant)

    def _lookup_binding(self, node: Node, name: str) -> VariableType | None:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.error(node, f"Variable {name!r} has not been declared")
        return None

    def _lookup_variable(self, node: Node, name: str) -> str | None:
        binding = self._lookup_binding(node, name)
        return binding.type_name if binding is not None else None

    def _function(self, node: Node) -> None:
        previous_return = self.current_return_type
        previous_types = self.type_parameters
        self.type_parameters = set(node.fields.get("type_parameters", []))
        self.current_return_type = node.fields["return_type"]
        self._push_scope()
        for parameter in node.fields["parameters"]:
            self._declare_variable(
                parameter, parameter.fields["name"], parameter.fields["type"]
            )
        self._block(node.fields["body"], create_scope=False)
        self._pop_scope()
        self.current_return_type = previous_return
        self.type_parameters = previous_types

    def _block(self, node: Node, create_scope: bool = True) -> None:
        if create_scope:
            self._push_scope()
        for statement in node.fields["statements"]:
            self._statement(statement)
        if create_scope:
            self._pop_scope()

    def _statement(self, node: Node) -> None:
        kind = node.kind
        if kind in {"VarDecl", "ConstDecl"}:
            declared_type = node.fields["type"]
            initializer = node.fields["initializer"]
            if initializer is not None:
                actual = self._expression(initializer)
                if actual is not None and actual != declared_type:
                    self.error(
                        initializer,
                        f"Cannot initialise {declared_type} variable with {actual}",
                    )
            self._declare_variable(node, node.fields["name"], declared_type,
                                   constant=kind == "ConstDecl")
            return
        if kind in {"Assign", "AssignIndex"}:
            binding = self._lookup_binding(node, node.fields["target"])
            target_type = binding.type_name if binding is not None else None
            if binding is not None and binding.constant:
                self.error(node, f"Cannot modify constant {node.fields['target']!r}")
            if kind == "AssignIndex":
                self._check_index(node.fields["index"])
                if target_type is not None:
                    if not target_type.endswith("[]"):
                        self.error(node, "Indexed assignment requires an array")
                        target_type = None
                    else:
                        target_type = target_type[:-2]
            value_type = self._expression(node.fields["value"])
            if (
                target_type is not None
                and value_type is not None
                and target_type != value_type
            ):
                self.error(node, f"Cannot assign {value_type} value to {target_type} variable")
            return
        if kind == "Print":
            self._expression(node.fields["value"])
            return
        if kind == "Return":
            actual = self._expression(node.fields["value"])
            if self.current_return_type is None:
                self.error(node, "return may only be used inside a function")
            elif actual is not None and actual != self.current_return_type:
                self.error(
                    node,
                    f"Function must return {self.current_return_type}, found {actual}",
                )
            return
        if kind == "If":
            self._condition(node.fields["condition"], "if")
            self._block(node.fields["then"])
            if node.fields["otherwise"] is not None:
                self._block(node.fields["otherwise"])
            return
        if kind == "While":
            self._condition(node.fields["condition"], "while")
            self._block(node.fields["body"])
            return
        self.error(node, f"Unknown statement node {kind!r}")

    def _condition(self, node: Node, owner: str) -> None:
        actual = self._expression(node)
        if actual is not None and actual != "bool":
            self.error(node, f"{owner} condition must have type bool, found {actual}")

    def _check_index(self, node: Node) -> None:
        actual = self._expression(node)
        if actual is not None and actual != "int":
            self.error(node, f"Array index must have type int, found {actual}")

    def _expression(self, node: Node, allow_min_magnitude: bool = False) -> str | None:
        kind = node.kind
        if kind == "Input":
            return "int"
        if kind == "Array":
            types = [self._expression(element) for element in node.fields["elements"]]
            element_type = next((t for t in types if t is not None), None)
            if element_type is None:
                return None
            if element_type not in {"int", "bool"} | self.type_parameters:
                self.error(node, "Only one-dimensional int or bool arrays are supported")
                return None
            if any(t is not None and t != element_type for t in types):
                self.error(node, "Array elements must have the same type")
            return element_type + "[]"
        if kind == "Index":
            array_type = self._expression(node.fields["array"])
            self._check_index(node.fields["index"])
            if array_type is None:
                return None
            if not array_type.endswith("[]"):
                self.error(node, "Indexing requires an array")
                return None
            return array_type[:-2]
        if kind == "Integer":
            limit = INT_MAX + 1 if allow_min_magnitude else INT_MAX
            # Compare decimal strings before converting: very long literals
            # can exceed Python's own integer conversion limit.
            digits = node.fields["decimal"].lstrip("0") or "0"
            bound = str(limit)
            if len(digits) > len(bound) or (len(digits) == len(bound) and digits > bound):
                self.error(node, "Integer literal is outside the signed 32-bit range")
            return "int"
        if kind == "Boolean":
            return "bool"
        if kind == "Variable":
            return self._lookup_variable(node, node.fields["name"])
        if kind == "Call":
            arguments = node.fields["arguments"]
            actual_types = [self._expression(argument) for argument in arguments]
            name = node.fields["name"]
            if name in {"array", "len", "collect"}:
                return self._builtin(node, actual_types)
            signature = self.functions.get(name)
            if signature is None:
                self.error(node, f"Function {node.fields['name']!r} has not been declared")
                return None
            if len(arguments) != len(signature.parameters):
                self.error(
                    node,
                    f"Function {node.fields['name']!r} expects "
                    f"{len(signature.parameters)} arguments, found {len(arguments)}",
                )
            bindings: dict[str, str] = {}
            for index, (expected, actual) in enumerate(
                zip(signature.parameters, actual_types), start=1
            ):
                generic = expected[:-2] if expected.endswith("[]") else expected
                if generic in signature.type_parameters and actual is not None:
                    candidate = actual
                    if expected.endswith("[]"):
                        candidate = actual[:-2] if actual.endswith("[]") else "<not an array>"
                    if candidate not in {"int", "bool"} | self.type_parameters:
                        self.error(arguments[index - 1], "Generic type arguments must be scalar int or bool")
                        continue
                    if generic not in bindings:
                        bindings[generic] = candidate
                    expected = bindings[generic] + ("[]" if expected.endswith("[]") else "")
                if actual is not None and actual != expected:
                    self.error(
                        arguments[index - 1],
                        f"Argument {index} must have type {expected}, found {actual}",
                    )
            result_base = signature.result.removesuffix("[]")
            if result_base in signature.type_parameters:
                inferred = bindings.get(result_base)
                if inferred is None:
                    return None
                return inferred + ("[]" if signature.result.endswith("[]") else "")
            return signature.result
        if kind == "Unary":
            operator = node.fields["operator"]
            operand_node = node.fields["operand"]
            operand = self._expression(
                operand_node,
                allow_min_magnitude=operator == "-" and operand_node.kind == "Integer",
            )
            expected = "int" if operator == "-" else "bool"
            if operand is not None and operand != expected:
                self.error(node, f"Operator {operator!r} requires {expected}, found {operand}")
            return expected
        if kind == "Binary":
            operator = node.fields["operator"]
            left = self._expression(node.fields["left"])
            right = self._expression(node.fields["right"])
            if operator in {"==", "!="}:
                if left is not None and right is not None and left != right:
                    self.error(node, f"Operator {operator!r} requires operands of the same type")
                return "bool"

            expected = "bool" if operator in {"and", "or"} else "int"
            for side, actual in (("left", left), ("right", right)):
                if actual is not None and actual != expected:
                    self.error(
                        node,
                        f"{side.capitalize()} operand of {operator!r} must be "
                        f"{expected}, found {actual}",
                    )
            return "bool" if operator in {"<", "<=", ">", ">=", "and", "or"} else "int"

        self.error(node, f"Unknown expression node {kind!r}")
        return None

    def _builtin(self, node: Node, types: list[str | None]) -> str | None:
        name = node.fields["name"]
        arity = {"array": 2, "len": 1, "collect": 0}[name]
        if len(types) != arity:
            self.error(node, f"Builtin {name!r} expects {arity} arguments, found {len(types)}")
            return None
        if name == "collect":
            return "int"
        if name == "len":
            if types[0] is not None and not types[0].endswith("[]"):
                self.error(node, "len requires an array")
            return "int"
        if types[0] is not None and types[0] != "int":
            self.error(node.fields["arguments"][0], "Array length must have type int")
        fill_type = types[1]
        if fill_type is None:
            return None
        if fill_type not in {"int", "bool"} | self.type_parameters:
            self.error(node.fields["arguments"][1], "Array fill must be scalar int or bool")
            return None
        return fill_type + "[]"


def analyse(program: Node) -> list[Diagnostic]:
    """Return all semantic diagnostics for *program*."""
    return SemanticAnalyzer().analyse(program)
