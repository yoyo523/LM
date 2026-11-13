import unittest
from klean import Parser, Token
from klean.lexer_adapter import tokenize


def parse(source):
    tokens, errors = tokenize(source)
    result = Parser(tokens).parse()
    return result, errors + result.diagnostics


class ParserTests(unittest.TestCase):
    def good(self, source):
        result, errors = parse(source)
        self.assertEqual(errors, [])
        return result.program.fields['items']

    def expression(self, source):
        return self.good(f'print({source});')[0].fields['value']

    def test_precedence(self):
        tree = self.expression('15 + 4 * 2')
        self.assertEqual(tree.fields['operator'], '+')
        self.assertEqual(tree.fields['right'].fields['operator'], '*')

    def test_parentheses(self):
        tree = self.expression('(15 + 4) * 2')
        self.assertEqual(tree.fields['operator'], '*')
        self.assertEqual(tree.fields['left'].fields['operator'], '+')

    def test_associativity(self):
        tree = self.expression('8 - 3 - 1')
        self.assertEqual(tree.fields['left'].fields['operator'], '-')

    def test_logical_precedence(self):
        tree = self.expression('true or false and not 1 + 2 * 3 < 8 == false')
        self.assertEqual(tree.fields['operator'], 'or')
        self.assertEqual(tree.fields['right'].fields['operator'], 'and')

    def test_declaration_and_assignment(self):
        items = self.good('let x: int; 15 + 4 * 2 -> x; print(x);')
        self.assertIsNone(items[0].fields['initializer'])
        self.assertEqual(items[1].fields['target'], 'x')

    def test_functions_and_recursion(self):
        items = self.good('fn fib(n: int) -> int { if (n <= 1) { return n; } return fib(n-1) + fib(n-2); } print(fib(8));')
        self.assertEqual(items[0].fields['parameters'][0].fields['type'], 'int')
        self.assertEqual(items[1].fields['value'].kind, 'Call')

    def test_empty_parameters_and_blocks(self):
        self.good('fn f() -> bool { return true; } if (f()) {} else {} while (false) {}')

    def test_multiple_arguments(self):
        tree = self.expression('f(1, g(2), true)')
        self.assertEqual(len(tree.fields['arguments']), 3)

    def test_bad_syntax(self):
        for source in ['print(1 < 2 < 3);', '1 -> 2;', 'If (true) {}',
                       'while (true) print(1);', 'let x: float;',
                       'print(f(1,));', 'print(1)', 'print((1);', 'print 1);',
                       'if (true) {',
                       'if (true) { fn f() -> int { return 1; } }']:
            with self.subTest(source=source):
                self.assertTrue(parse(source)[1])

    def test_recovery_at_next_statement(self):
        result, errors = parse('let x: int = ; print(23); print(); print(6);')
        self.assertEqual(len(errors), 2)
        self.assertEqual([n.fields['value'].fields['decimal'] for n in result.program.fields['items']], ['23', '6'])

    def test_missing_semicolon_preserves_next_statement(self):
        result, errors = parse('let x: int = 1\nprint(23);')
        self.assertEqual(len(errors), 1)
        self.assertEqual(result.program.fields['items'][0].kind, 'Print')

    def test_block_recovery_and_unmatched_brace(self):
        result, errors = parse('if (true) { print(1) } print(2); } print(3);')
        self.assertEqual(len(errors), 2)
        self.assertEqual([n.kind for n in result.program.fields['items']], ['If', 'Print', 'Print'])

    def test_source_locations_and_lexical_errors(self):
        tokens, errors = tokenize('// comment\n  print(@);\n')
        self.assertEqual((tokens[0].line, tokens[0].column), (2, 3))
        self.assertEqual((errors[0].line, errors[0].column), (2, 9))
        self.assertEqual((tokens[-1].line, tokens[-1].column), (3, 1))

    def test_semantic_errors_are_not_syntax_errors(self):
        self.good('return true; 10 -> unknown; if (1) {} print(true + 5);')

    def test_eof_contract(self):
        for tokens in [[], [Token('ID', 'x', 1, 1)], [Token('EOF', '', 1, 1), Token('EOF', '', 1, 1)]]:
            with self.assertRaises(ValueError):
                Parser(tokens)

    def test_empty_program(self):
        self.assertEqual(self.good(''), [])


if __name__ == '__main__':
    unittest.main()
