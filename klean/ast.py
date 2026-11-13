"""Source-positioned syntax tree. No evaluation or type checking occurs here."""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    line: int
    column: int


@dataclass
class Node:
    """AST record; fields are specified in docs/parser_contract.md.

    The anchor token locates the construct. Function/VarDecl/ConstDecl carry
    name_token; Assign/AssignIndex carry target_token for precise name diagnostics.
    Consumers must reject trees accompanied by lexer or parser diagnostics.
    """
    kind: str
    token: Token
    fields: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Diagnostic:
    line: int
    column: int
    message: str


@dataclass
class ParseResult:
    """Program plus diagnostics; an erroneous Program is for inspection only."""
    program: Node
    diagnostics: list[Diagnostic]
