"""Public compiler pipeline for Klean source text."""
from __future__ import annotations

from dataclasses import dataclass

from .ast import Diagnostic, Node, Token
from .bytecode import BytecodeProgram
from .codegen import generate
from .lexer_adapter import tokenize
from .parser import Parser
from .semantic import analyse


@dataclass
class CompilationResult:
    tokens: list[Token]
    ast: Node
    bytecode: BytecodeProgram | None
    diagnostics: list[Diagnostic]


def compile_source(source: str) -> CompilationResult:
    tokens, diagnostics = tokenize(source)
    parsed = Parser(tokens).parse()
    diagnostics.extend(parsed.diagnostics)
    bytecode = None
    if not diagnostics:
        diagnostics.extend(analyse(parsed.program))
    if not diagnostics:
        bytecode = generate(parsed.program)
    diagnostics.sort(key=lambda item: (item.line, item.column, item.message))
    return CompilationResult(tokens, parsed.program, bytecode, diagnostics)
