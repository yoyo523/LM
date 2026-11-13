"""Small reference scanner for exercising the parser before lexer integration.

The lexer owner may replace this module while retaining the Token contract.
"""
import re
from .ast import Diagnostic, Token

KEYWORDS = set('let int bool if else while fn return print true false and or not'.split())
PATTERN = re.compile(r'(?P<SPACE>[ \t\r]+)|(?P<NEWLINE>\n)|(?P<COMMENT>//[^\n]*)|(?P<INT_LIT>[0-9]+)|(?P<ID>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<SYMBOL>->|<=|>=|==|!=|[+*/<>=:;,(){}-])|(?P<INVALID>.)')


def tokenize(source: str) -> tuple[list[Token], list[Diagnostic]]:
    tokens, diagnostics = [], []
    line, line_start = 1, 0
    for match in PATTERN.finditer(source):
        kind, text = match.lastgroup, match.group()
        # Every alternative in PATTERN is named, so a successful match always
        # has a token kind. Keep the invariant explicit for static type checks.
        assert kind is not None
        column = match.start() - line_start + 1
        if kind == 'NEWLINE':
            line += 1
            line_start = match.end()
        elif kind in {'SPACE', 'COMMENT'}:
            continue
        elif kind == 'INVALID':
            diagnostics.append(Diagnostic(line, column, f'Illegal character {text!r}'))
        else:
            if kind == 'SYMBOL' or kind == 'ID' and text in KEYWORDS:
                kind = text
            tokens.append(Token(kind, text, line, column))
    tokens.append(Token('EOF', '', line, len(source) - line_start + 1))
    return tokens, diagnostics
