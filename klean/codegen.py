"""Translate a semantically valid Klean AST into stack bytecode."""
from __future__ import annotations

from .ast import Node
from .bytecode import BytecodeProgram, FunctionCode, Instruction


class CodeGenerator:
    def __init__(self) -> None:
        self.instructions: list[Instruction | tuple[str, str]] = []
        self.label_number = 0

    def generate(self, program: Node) -> BytecodeProgram:
        functions: dict[str, FunctionCode] = {}
        main_nodes = []
        for item in program.fields["items"]:
            if item.kind == "Function":
                functions[item.fields["name"]] = self._function(item)
            else:
                main_nodes.append(item)

        self.instructions = []
        for statement in main_nodes:
            self._statement(statement)
        self._emit("HALT", node=program)
        return BytecodeProgram(self._resolve_labels(), functions)

    def _function(self, node: Node) -> FunctionCode:
        previous = self.instructions
        self.instructions = []
        self._block(node.fields["body"], scoped=False)
        self._emit("MISSING_RETURN", node=node)
        instructions = self._resolve_labels()
        self.instructions = previous
        return FunctionCode(
            node.fields["name"],
            [parameter.fields["name"] for parameter in node.fields["parameters"]],
            instructions,
        )

    def _new_label(self, prefix: str) -> str:
        self.label_number += 1
        return f"{prefix}_{self.label_number}"

    def _mark(self, label: str) -> None:
        self.instructions.append(("LABEL", label))

    def _emit(self, operation: str, argument=None, node: Node | None = None) -> None:
        line = node.token.line if node is not None else 0
        column = node.token.column if node is not None else 0
        self.instructions.append(Instruction(operation, argument, line, column))

    def _resolve_labels(self) -> list[Instruction]:
        labels: dict[str, int] = {}
        position = 0
        for entry in self.instructions:
            if isinstance(entry, tuple):
                labels[entry[1]] = position
            else:
                position += 1
        result = []
        for entry in self.instructions:
            if isinstance(entry, tuple):
                continue
            if entry.operation in {"JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE"}:
                entry = Instruction(
                    entry.operation,
                    labels[entry.argument],
                    entry.line,
                    entry.column,
                )
            result.append(entry)
        return result

    def _block(self, node: Node, scoped: bool = True) -> None:
        if scoped:
            self._emit("ENTER_SCOPE", node=node)
        for statement in node.fields["statements"]:
            self._statement(statement)
        if scoped:
            self._emit("EXIT_SCOPE", node=node)

    def _statement(self, node: Node) -> None:
        kind = node.kind
        if kind == "VarDecl":
            initializer = node.fields["initializer"]
            if initializer is None:
                self._emit("PUSH_UNINITIALISED", node=node)
            else:
                self._expression(initializer)
            self._emit("DECLARE", node.fields["name"], node)
            return
        if kind == "Assign":
            self._expression(node.fields["value"])
            self._emit("STORE", node.fields["target"], node)
            return
        if kind == "Print":
            self._expression(node.fields["value"])
            self._emit("PRINT", node=node)
            return
        if kind == "Return":
            self._expression(node.fields["value"])
            self._emit("RETURN", node=node)
            return
        if kind == "If":
            else_label = self._new_label("else")
            end_label = self._new_label("endif")
            self._expression(node.fields["condition"])
            self._emit("JUMP_IF_FALSE", else_label, node)
            self._block(node.fields["then"])
            self._emit("JUMP", end_label, node)
            self._mark(else_label)
            if node.fields["otherwise"] is not None:
                self._block(node.fields["otherwise"])
            self._mark(end_label)
            return
        if kind == "While":
            start_label = self._new_label("while")
            end_label = self._new_label("endwhile")
            self._mark(start_label)
            self._expression(node.fields["condition"])
            self._emit("JUMP_IF_FALSE", end_label, node)
            self._block(node.fields["body"])
            self._emit("JUMP", start_label, node)
            self._mark(end_label)
            return
        raise ValueError(f"Unknown statement node {kind!r}")

    def _expression(self, node: Node) -> None:
        kind = node.kind
        if kind == "Integer":
            self._emit("PUSH", int(node.fields["decimal"]), node)
            return
        if kind == "Boolean":
            self._emit("PUSH", node.fields["value"], node)
            return
        if kind == "Variable":
            self._emit("LOAD", node.fields["name"], node)
            return
        if kind == "Call":
            for argument in node.fields["arguments"]:
                self._expression(argument)
            self._emit("CALL", (node.fields["name"], len(node.fields["arguments"])), node)
            return
        if kind == "Unary":
            operand = node.fields["operand"]
            if node.fields["operator"] == "-" and operand.kind == "Integer":
                self._emit("PUSH", -int(operand.fields["decimal"]), node)
            else:
                self._expression(operand)
                self._emit("NEG" if node.fields["operator"] == "-" else "NOT", node=node)
            return
        if kind == "Binary":
            operator = node.fields["operator"]
            if operator == "and":
                false_label = self._new_label("and_false")
                end_label = self._new_label("and_end")
                self._expression(node.fields["left"])
                self._emit("JUMP_IF_FALSE", false_label, node)
                self._expression(node.fields["right"])
                self._emit("JUMP", end_label, node)
                self._mark(false_label)
                self._emit("PUSH", False, node)
                self._mark(end_label)
                return
            if operator == "or":
                true_label = self._new_label("or_true")
                end_label = self._new_label("or_end")
                self._expression(node.fields["left"])
                self._emit("JUMP_IF_TRUE", true_label, node)
                self._expression(node.fields["right"])
                self._emit("JUMP", end_label, node)
                self._mark(true_label)
                self._emit("PUSH", True, node)
                self._mark(end_label)
                return
            self._expression(node.fields["left"])
            self._expression(node.fields["right"])
            operations = {
                "+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV",
                "==": "EQ", "!=": "NE", "<": "LT", "<=": "LE",
                ">": "GT", ">=": "GE",
            }
            self._emit(operations[operator], node=node)
            return
        raise ValueError(f"Unknown expression node {kind!r}")


def generate(program: Node) -> BytecodeProgram:
    return CodeGenerator().generate(program)
