"""A checked 32-bit stack virtual machine for Klean bytecode."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .bytecode import BytecodeProgram, FunctionCode, Instruction
from .semantic import INT_MAX, INT_MIN


class KleanRuntimeError(RuntimeError):
    def __init__(self, message: str, instruction: Instruction | None = None):
        if instruction is not None and instruction.line:
            message = f"{instruction.line}:{instruction.column}: {message}"
        super().__init__(message)


UNINITIALISED = object()


@dataclass
class Frame:
    name: str
    code: list[Instruction]
    ip: int
    scopes: list[dict[str, object]]
    return_code: list[Instruction] | None = None
    return_ip: int | None = None


class VirtualMachine:
    def __init__(self, program: BytecodeProgram, output: Callable[[str], None] = print):
        self.program = program
        self.output = output
        self.stack: list[object] = []
        self.global_scope: dict[str, object] = {}
        self.frames: list[Frame] = [Frame("<main>", program.main, 0, [self.global_scope])]

    @property
    def frame(self) -> Frame:
        return self.frames[-1]

    def run(self) -> None:
        while self.frames:
            frame = self.frame
            if frame.ip >= len(frame.code):
                raise KleanRuntimeError(f"Execution left {frame.name!r} without HALT or RETURN")
            instruction = frame.code[frame.ip]
            frame.ip += 1
            self._execute(instruction)

    def _pop(self, instruction: Instruction) -> object:
        if not self.stack:
            raise KleanRuntimeError("Operand stack underflow", instruction)
        return self.stack.pop()

    def _checked_int(self, value: int, instruction: Instruction) -> int:
        if value < INT_MIN or value > INT_MAX:
            raise KleanRuntimeError("32-bit integer overflow", instruction)
        return value

    def _lookup_scope(self, name: str, instruction: Instruction) -> dict[str, object]:
        for scope in reversed(self.frame.scopes):
            if name in scope:
                return scope
        if self.frame.name != "<main>" and name in self.global_scope:
            return self.global_scope
        raise KleanRuntimeError(f"Variable {name!r} is not available", instruction)

    def _execute(self, ins: Instruction) -> None:
        op = ins.operation
        if op == "PUSH":
            if type(ins.argument) is int:
                self._checked_int(ins.argument, ins)
            self.stack.append(ins.argument)
        elif op == "PUSH_UNINITIALISED":
            self.stack.append(UNINITIALISED)
        elif op == "DECLARE":
            scope = self.frame.scopes[-1]
            if ins.argument in scope:
                raise KleanRuntimeError(f"Variable {ins.argument!r} already exists", ins)
            scope[ins.argument] = self._pop(ins)
        elif op == "LOAD":
            value = self._lookup_scope(ins.argument, ins)[ins.argument]
            if value is UNINITIALISED:
                raise KleanRuntimeError(f"Variable {ins.argument!r} is uninitialised", ins)
            self.stack.append(value)
        elif op == "STORE":
            self._lookup_scope(ins.argument, ins)[ins.argument] = self._pop(ins)
        elif op == "ENTER_SCOPE":
            self.frame.scopes.append({})
        elif op == "EXIT_SCOPE":
            if len(self.frame.scopes) <= 1:
                raise KleanRuntimeError("Cannot leave the function scope", ins)
            self.frame.scopes.pop()
        elif op == "PRINT":
            value = self._pop(ins)
            self.output(str(value).lower() if type(value) is bool else str(value))
        elif op == "NEG":
            self.stack.append(self._checked_int(-int(self._pop(ins)), ins))
        elif op == "NOT":
            self.stack.append(not bool(self._pop(ins)))
        elif op in {"ADD", "SUB", "MUL", "DIV"}:
            right, left = int(self._pop(ins)), int(self._pop(ins))
            if op == "ADD":
                value = left + right
            elif op == "SUB":
                value = left - right
            elif op == "MUL":
                value = left * right
            else:
                if right == 0:
                    raise KleanRuntimeError("Division by zero", ins)
                value = abs(left) // abs(right)
                if (left < 0) != (right < 0):
                    value = -value
            self.stack.append(self._checked_int(value, ins))
        elif op in {"EQ", "NE", "LT", "LE", "GT", "GE"}:
            right, left = self._pop(ins), self._pop(ins)
            operations = {
                "EQ": lambda: left == right,
                "NE": lambda: left != right,
                "LT": lambda: left < right,
                "LE": lambda: left <= right,
                "GT": lambda: left > right,
                "GE": lambda: left >= right,
            }
            self.stack.append(operations[op]())
        elif op == "JUMP":
            self.frame.ip = ins.argument
        elif op in {"JUMP_IF_FALSE", "JUMP_IF_TRUE"}:
            condition = bool(self._pop(ins))
            if condition == (op == "JUMP_IF_TRUE"):
                self.frame.ip = ins.argument
        elif op == "CALL":
            name, argument_count = ins.argument
            function = self.program.functions.get(name)
            if function is None:
                raise KleanRuntimeError(f"Function {name!r} does not exist", ins)
            arguments = [self._pop(ins) for _ in range(argument_count)][::-1]
            scope = dict(zip(function.parameters, arguments))
            caller = self.frame
            self.frames.append(
                Frame(name, function.instructions, 0, [scope], caller.code, caller.ip)
            )
        elif op == "RETURN":
            value = self._pop(ins)
            finished = self.frames.pop()
            if not self.frames:
                raise KleanRuntimeError("RETURN executed outside a function", ins)
            caller = self.frame
            caller.code = finished.return_code or caller.code
            caller.ip = finished.return_ip if finished.return_ip is not None else caller.ip
            self.stack.append(value)
        elif op == "MISSING_RETURN":
            raise KleanRuntimeError(f"Function {self.frame.name!r} finished without return", ins)
        elif op == "HALT":
            if self.frame.name != "<main>":
                raise KleanRuntimeError("HALT inside a function", ins)
            self.frames.pop()
        else:
            raise KleanRuntimeError(f"Unknown bytecode operation {op!r}", ins)


def execute(program: BytecodeProgram, output: Callable[[str], None] = print) -> None:
    VirtualMachine(program, output).run()
