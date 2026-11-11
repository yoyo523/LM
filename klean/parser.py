"""Recursive descent parser for the Assignment 2a Klean grammar."""
from __future__ import annotations

from .ast import Diagnostic, Node, ParseResult, Token


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        if not tokens or tokens[-1].kind != 'EOF':
            raise ValueError('Token stream must end in EOF')
        if any(t.kind == 'EOF' for t in tokens[:-1]):
            raise ValueError('EOF must occur only at the end')
        self.tokens = tokens
        self.position = 0
        self.diagnostics: list[Diagnostic] = []

    @property
    def current(self) -> Token:
        return self.tokens[self.position]

    def take(self) -> Token:
        token = self.current
        if token.kind != 'EOF':
            self.position += 1
        return token

    def accept(self, kind: str) -> Token | None:
        return self.take() if self.current.kind == kind else None

    def expect(self, kind: str) -> Token:
        if self.current.kind != kind:
            self.fail(f'Expected {kind!r}, found {self.current.text!r}')
        return self.take()

    def fail(self, message: str):
        t = self.current
        self.diagnostics.append(Diagnostic(t.line, t.column, message))
        raise ParseError(message)

    def node(self, kind: str, token: Token, **fields) -> Node:
        return Node(kind, token, fields)

    def parse(self) -> ParseResult:
        start = self.current
        return ParseResult(self.node('Program', start, items=self.items(False)), self.diagnostics)

    def items(self, in_block: bool) -> list[Node]:
        result = []
        while self.current.kind != 'EOF' and not (in_block and self.current.kind == '}'):
            start = self.position
            try:
                if self.current.kind == 'fn':
                    if in_block:
                        self.fail('Functions may only be declared at top level')
                    result.append(self.function())
                else:
                    result.append(self.statement())
            except ParseError:
                self.synchronize(start, in_block)
        return result

    def synchronize(self, start: int, in_block: bool):
        # Leave a containing block's closing brace for block(), but always
        # consume an unmatched top-level brace to guarantee progress.
        while self.current.kind != 'EOF':
            if self.current.kind == '}':
                if not in_block:
                    self.take()
                return
            if self.accept(';'):
                return
            if self.position > start and self.current.kind in {'let', 'if', 'while', 'return', 'print', 'fn'}:
                return
            self.take()

    def type_name(self) -> str:
        if self.current.kind not in {'int', 'bool'}:
            self.fail('Expected type int or bool')
        return self.take().kind

    def block(self) -> Node:
        token = self.expect('{')
        body = self.items(True)
        self.expect('}')
        return self.node('Block', token, statements=body)

    def function(self) -> Node:
        token = self.expect('fn')
        name = self.expect('ID').text
        self.expect('(')
        params = []
        if self.current.kind != ')':
            while True:
                param = self.expect('ID')
                self.expect(':')
                params.append(self.node('Parameter', param, name=param.text, type=self.type_name()))
                if not self.accept(','):
                    break
        self.expect(')')
        self.expect('->')
        return_type = self.type_name()
        return self.node('Function', token, name=name, parameters=params,
                         return_type=return_type, body=self.block())

    def statement(self) -> Node:
        token = self.current
        if self.accept('let'):
            name = self.expect('ID').text
            self.expect(':')
            type_name = self.type_name()
            value = self.expression() if self.accept('=') else None
            self.expect(';')
            return self.node('VarDecl', token, name=name, type=type_name, initializer=value)
        if self.current.kind in {'if', 'while'}:
            keyword = self.take().kind
            self.expect('(')
            condition = self.expression()
            self.expect(')')
            body = self.block()
            if keyword == 'while':
                return self.node('While', token, condition=condition, body=body)
            alternative = self.block() if self.accept('else') else None
            return self.node('If', token, condition=condition, then=body, otherwise=alternative)
        if self.accept('return'):
            value = self.expression()
            self.expect(';')
            return self.node('Return', token, value=value)
        if self.accept('print'):
            self.expect('(')
            value = self.expression()
            self.expect(')')
            self.expect(';')
            return self.node('Print', token, value=value)
        value = self.expression()
        self.expect('->')
        target = self.expect('ID')
        self.expect(';')
        return self.node('Assign', token, value=value, target=target.text)

    # Lowest to highest precedence. Only the relational level permits at
    # most one operator, exactly as specified in the report.
    LEVELS = ({'or'}, {'and'}, {'==', '!='}, {'<', '<=', '>', '>='}, {'+', '-'}, {'*', '/'})

    def expression(self, level: int = 0) -> Node:
        if level == len(self.LEVELS):
            return self.factor()
        left = self.expression(level + 1)
        while self.current.kind in self.LEVELS[level]:
            operator = self.take()
            right = self.expression(level + 1)
            left = self.node('Binary', operator, operator=operator.kind, left=left, right=right)
            if level == 3:
                break
        return left

    def factor(self) -> Node:
        if self.current.kind in {'-', 'not'}:
            token = self.take()
            return self.node('Unary', token, operator=token.kind, operand=self.factor())
        token = self.current
        if self.accept('INT_LIT'):
            # Preserve decimal text: range and signed-minimum handling belong
            # to the semantic stage, not Python's arbitrary precision integers.
            return self.node('Integer', token, decimal=token.text)
        if self.current.kind in {'true', 'false'}:
            self.take()
            return self.node('Boolean', token, value=token.kind == 'true')
        if self.accept('ID'):
            if not self.accept('('):
                return self.node('Variable', token, name=token.text)
            arguments = []
            if self.current.kind != ')':
                while True:
                    arguments.append(self.expression())
                    if not self.accept(','):
                        break
            self.expect(')')
            return self.node('Call', token, name=token.text, arguments=arguments)
        if self.accept('('):
            expression = self.expression()
            self.expect(')')
            return expression
        self.fail(f'Expected expression, found {token.text!r}')
