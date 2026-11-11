"""Learning demo: observe token operations in the existing Parser.

Run from the project root: python3 -m examples.parser_basics
"""
from klean import Parser
from klean.lexer_adapter import tokenize
from klean.parser import ParseError


def show(parser, label):
    token = parser.current
    print(f'{label}: position={parser.position}, '
          f'kind={token.kind!r}, text={token.text!r}, '
          f'location={token.line}:{token.column}')


def main():
    tokens, errors = tokenize('print(23);')
    assert not errors
    parser = Parser(tokens)
    print('1. Inspect, consume, and check then consume')
    show(parser, 'Initial state')
    print('Read current:', parser.current)
    show(parser, 'After inspection (position unchanged)')
    print('take returns:', parser.take())
    show(parser, 'After consuming print')
    print("expect('(') returns:", parser.expect('('))
    show(parser, 'After matching the opening parenthesis')

    print('\n2. Location and diagnostic on a failed match')
    try:
        parser.expect(')')  # Deliberate mismatch: the current token is 23.
    except ParseError:
        error = parser.diagnostics[-1]
        print(f'{error.line}:{error.column}: {error.message}')
    show(parser, 'After the failed match (position unchanged)')

    print('\n3. Parse the same tokens from the beginning to build an AST')
    result = Parser(tokens).parse()  # A new instance starts at position=0.
    print(result.program)
    print('Syntax diagnostics:', result.diagnostics)


if __name__ == '__main__':
    main()
