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
    parser = Parser(tokens)
    program = Node("Program", tokens[0], {"items": []})
    bytecode = None
    try:
        parsed = parser.parse()
        program = parsed.program
        diagnostics.extend(parsed.diagnostics)
        if not diagnostics:
            diagnostics.extend(analyse(program))
        if not diagnostics:
            bytecode = generate(program)
    except RecursionError:
        token = parser.current
        diagnostics.append(Diagnostic(token.line, token.column,
                                      "Program nesting exceeds the compiler recursion limit"))
    diagnostics.sort(key=lambda item: (item.line, item.column, item.message))
    return CompilationResult(tokens, program, bytecode, diagnostics)
