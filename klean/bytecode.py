"""Bytecode data structures used by the Klean compiler and virtual machine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Instruction:
    operation: str
    argument: Any = None
    line: int = 0
    column: int = 0

    def __str__(self) -> str:
        suffix = "" if self.argument is None else f" {self.argument!r}"
        return f"{self.operation}{suffix}"


@dataclass
class FunctionCode:
    name: str
    parameters: list[str]
    instructions: list[Instruction]


@dataclass
class BytecodeProgram:
    main: list[Instruction]
    functions: dict[str, FunctionCode] = field(default_factory=dict)

    def format(self) -> str:
        lines = ["[main]"]
        lines.extend(f"{i:04d}  {instruction}" for i, instruction in enumerate(self.main))
        for function in self.functions.values():
            lines.append(f"\n[function {function.name}({', '.join(function.parameters)})]")
            lines.extend(
                f"{i:04d}  {instruction}"
                for i, instruction in enumerate(function.instructions)
            )
        return "\n".join(lines)
