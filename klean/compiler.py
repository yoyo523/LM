"""Public compiler pipeline for Klean source text."""
from __future__ import annotations

from dataclasses import dataclass

from .ast import Diagnostic, Node, Token
from .bytecode import BytecodeProgram
from .codegen import generate
from .lexer_adapter import tokenize
from .parser import Parser
from .optimizer import OptimizationStats, Optimizer
from .semantic import analyse


@dataclass
class CompilationResult:
    tokens: list[Token]
    ast: Node
    bytecode: BytecodeProgram | None
    diagnostics: list[Diagnostic]
    optimized_ast: Node | None = None
    optimization_stats: OptimizationStats | None = None


def compile_source(source: str, *, optimize: bool = True) -> CompilationResult:
    tokens, diagnostics = tokenize(source)
    parser = Parser(tokens)
    program = Node("Program", tokens[0], {"items": []})
    bytecode = None
    optimized_ast = None
    optimization_stats = None
    try:
        parsed = parser.parse()
        program = parsed.program
        diagnostics.extend(parsed.diagnostics)
        if not diagnostics:
            diagnostics.extend(analyse(program))
        if not diagnostics:
            if optimize:
                optimizer = Optimizer()
                optimized_ast = optimizer.optimize(program)
                optimization_stats = optimizer.stats
            bytecode = generate(optimized_ast if optimized_ast is not None else program)
    except RecursionError:
        token = parser.current
        diagnostics.append(Diagnostic(token.line, token.column,
                                      "Program nesting exceeds the compiler recursion limit"))
    diagnostics.sort(key=lambda item: (item.line, item.column, item.message))
    return CompilationResult(tokens, program, bytecode, diagnostics,
                             optimized_ast, optimization_stats)
