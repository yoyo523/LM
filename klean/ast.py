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
    program: Node
    diagnostics: list[Diagnostic]
