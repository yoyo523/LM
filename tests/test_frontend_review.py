"""Frontend-only structural checks: no semantic analyser or VM dependency."""
import unittest

from klean.ast import Token
from klean.lexer_adapter import tokenize
from klean.parser import Parser


class FrontendReviewTests(unittest.TestCase):
    def parse(self, source):
        tokens, errors = tokenize(source)
        self.assertEqual(errors, [])
        result = Parser(tokens).parse()
        self.assertEqual(result.diagnostics, [])
        return result.program.fields['items']

    def test_every_precedence_level_in_ast(self):
        tree = self.parse('print(true or false and 1 == 2 < 3 + 4 * -5);')[0].fields['value']
        # Syntax only: operand type validity belongs to the semantic stage.
        for operator in ['or', 'and', '==', '<', '+', '*']:
            self.assertEqual(tree.kind, 'Binary')
            self.assertEqual(tree.fields['operator'], operator)
            tree = tree.fields['right']
        self.assertEqual(tree.kind, 'Unary')
        self.assertEqual(tree.fields['operator'], '-')
        self.assertEqual(tree.fields['operand'].fields['decimal'], '5')

    def test_binary_left_and_unary_right_associativity(self):
        for expression, operator in [('9 / 3 / 1', '/'), ('3 == 2 == 1', '=='),
                                     ('true or false or true', 'or')]:
            with self.subTest(expression=expression):
                tree = self.parse(f'print({expression});')[0].fields['value']
                self.assertEqual(tree.fields['operator'], operator)
                self.assertEqual(tree.fields['left'].fields['operator'], operator)
        tree = self.parse('print(not - -1);')[0].fields['value']
        for operator in ['not', '-', '-']:
            self.assertEqual(tree.fields['operator'], operator)
            tree = tree.fields['operand']
        self.assertEqual(tree.kind, 'Integer')

    def test_control_flow_and_function_shapes(self):
        function, assignment = self.parse('''
        fn f(x: int, flag: bool) -> int {
            while (flag) {
                if (x > 0) { return x; } else { x + 1 -> x; }
            }
            return 0;
        }
        f(2, true) -> answer;
        ''')
        self.assertEqual(function.fields['name'], 'f')
        self.assertEqual(function.fields['return_type'], 'int')
        self.assertEqual([p.fields['type'] for p in function.fields['parameters']], ['int', 'bool'])
        loop, final_return = function.fields['body'].fields['statements']
        self.assertEqual(loop.kind, 'While')
        branch = loop.fields['body'].fields['statements'][0]
        self.assertEqual(branch.kind, 'If')
        self.assertEqual(branch.fields['then'].fields['statements'][0].kind, 'Return')
        self.assertEqual(branch.fields['otherwise'].fields['statements'][0].kind, 'Assign')
        self.assertEqual(final_return.kind, 'Return')
        self.assertEqual(assignment.fields['value'].kind, 'Call')
        self.assertEqual(assignment.fields['target'], 'answer')

    def test_complex_arguments_without_backend(self):
        call = self.parse('print(f(g(1, h()), (2 + 3) * 4, not false and true));')[0].fields['value']
        first, second, third = call.fields['arguments']
        self.assertEqual(first.fields['arguments'][1].fields['arguments'], [])
        self.assertEqual(second.fields['operator'], '*')
        self.assertEqual(second.fields['left'].fields['operator'], '+')
        self.assertEqual(third.fields['operator'], 'and')
        self.assertEqual(third.fields['left'].fields['operator'], 'not')

    def test_every_token_prefix_terminates_at_eof(self):
        tokens, errors = tokenize('fn f(x: int) -> int { if (x > 0) { return f(x-1); } else { return 0; } } print(f(2));')
        self.assertEqual(errors, [])
        for length in range(len(tokens)):
            with self.subTest(length=length):
                boundary = tokens[length]
                parser = Parser(tokens[:length] + [Token('EOF', '', boundary.line, boundary.column)])
                result = parser.parse()
                self.assertEqual(parser.current.kind, 'EOF')
                self.assertEqual(result.program.kind, 'Program')
                for diagnostic in result.diagnostics:
                    self.assertLessEqual((diagnostic.line, diagnostic.column),
                                         (boundary.line, boundary.column))

    def test_many_ast_nodes_without_backend(self):
        items = self.parse('let value: int;' * 3000)
        self.assertEqual(len(items), 3000)
        self.assertEqual(items[-1].fields['name_token'].text, 'value')

    def test_expression_and_block_depth_without_backend(self):
        for source in ['print(' + '-' * 2000 + '1);',
                       'if (true) {' * 2000 + '}' * 2000]:
            with self.subTest(prefix=source[:20]):
                tokens, errors = tokenize(source)
                self.assertEqual(errors, [])
                result = Parser(tokens).parse()
                self.assertEqual(result.program.fields['items'], [])
                self.assertIn('recursion limit', result.diagnostics[-1].message)
