"""Parser/AST contract checks shared by lexer and downstream consumers."""
from dataclasses import asdict
import json
import unittest

from klean import Parser, Token
from klean.compiler import compile_source
from klean.lexer_adapter import tokenize
from klean.vm import execute


def parse(source):
    tokens, errors = tokenize(source)
    assert not errors, errors
    return Parser(tokens).parse()


class ParserContractTests(unittest.TestCase):
    def test_identifier_tokens_and_json(self):
        result = parse('let value: int;\n2 -> value;\nfn f() -> int { return 1; }')
        declaration, assignment, function = result.program.fields['items']
        self.assertEqual(declaration.fields['name_token'], Token('ID', 'value', 1, 5))
        self.assertEqual(assignment.fields['target_token'], Token('ID', 'value', 2, 6))
        self.assertEqual(function.fields['name_token'], Token('ID', 'f', 3, 4))
        data = json.loads(json.dumps(asdict(result.program)))
        self.assertEqual(data['fields']['items'][1]['fields']['target_token']['column'], 6)

    def test_semantic_identifier_locations(self):
        cases = [
            ('1 -> missing;', 1, 6),
            ('let x: int;\nlet x: int;', 2, 5),
            ('fn f() -> int {return 1;}\nfn f() -> int {return 2;}', 2, 4),
            ('let x: int;\ntrue -> x;', 2, 9),
        ]
        for source, line, column in cases:
            with self.subTest(source=source):
                result = compile_source(source)
                self.assertIsNone(result.bytecode)
                self.assertEqual(len(result.diagnostics), 1)
                self.assertEqual((result.diagnostics[0].line, result.diagnostics[0].column),
                                 (line, column))

    def test_nested_function_recovery_preserves_scope(self):
        result = parse('if (true) { fn bad() -> int { if (true) { return 1; } } print(2); } print(3);')
        self.assertEqual(len(result.diagnostics), 1)
        condition, last = result.program.fields['items']
        body = condition.fields['then'].fields['statements']
        self.assertEqual([node.kind for node in body], ['Print'])
        self.assertEqual(body[0].fields['value'].fields['decimal'], '2')
        self.assertEqual(last.fields['value'].fields['decimal'], '3')

    def test_malformed_function_header_recovery(self):
        result = parse('fn bad(x int) -> int { if (true) { return 1; } } print(3);')
        self.assertEqual(len(result.diagnostics), 1)
        self.assertEqual([n.kind for n in result.program.fields['items']], ['Print'])

    def test_consecutive_errors_inside_block(self):
        result = parse('if (true) { print(); let a: int = ; print(7); } print(); print(8);')
        self.assertEqual(len(result.diagnostics), 3)
        items = result.program.fields['items']
        self.assertEqual(items[0].fields['then'].fields['statements'][0].fields['value'].fields['decimal'], '7')
        self.assertEqual(items[1].fields['value'].fields['decimal'], '8')

    def test_eof_at_incomplete_constructs(self):
        for source in ['fn f(', 'fn f(x: int', 'fn f() ->', 'if (true) {',
                       'print(f(1,', 'let x: int =', '1 ->', 'print(1)']:
            with self.subTest(source=source):
                result = parse(source)
                self.assertTrue(result.diagnostics)
                self.assertTrue(all('end of input' in d.message or 'Expected type' in d.message
                                    for d in result.diagnostics))
                self.assertEqual(result.diagnostics[-1].column, len(source) + 1)

    def test_direct_parser_depth_limit(self):
        result = parse('print(' + '(' * 2000 + '1' + ')' * 2000 + ');')
        self.assertEqual(result.program.fields['items'], [])
        self.assertIn('recursion limit', result.diagnostics[-1].message)

    def test_valid_nested_blocks(self):
        result = compile_source('if (true) {' * 20 + 'print(7);' + '}' * 20)
        self.assertEqual(result.diagnostics, [])
        output = []
        execute(result.bytecode, output.append)
        self.assertEqual(output, ['7'])

    def test_complex_calls_recursion_scope_and_return(self):
        source = '''
        fn sum(n: int) -> int {
            if (n == 0) { return 0; }
            return n + sum(n - 1);
        }
        fn choose(a: int, b: int, flag: bool) -> int {
            if (flag) { let a: int = a + 1; return a; }
            return b;
        }
        let a: int = 100;
        print(choose(sum(4), (2 + 3) * 4, not false and 2 < 3));
        print(choose(1, sum(3), false));
        print(a);
        '''
        result = compile_source(source)
        self.assertEqual(result.diagnostics, [])
        call = result.ast.fields['items'][3].fields['value']
        self.assertEqual(call.kind, 'Call')
        self.assertEqual([n.kind for n in call.fields['arguments']], ['Call', 'Binary', 'Binary'])
        output = []
        execute(result.bytecode, output.append)
        self.assertEqual(output, ['11', '6', '100'])

    def test_lexer_kinds_and_maximal_symbols(self):
        source = 'let int bool if else while fn return print true false and or not name 123 -> <= >= == != + - * / < > = : ; , ( ) { }'
        tokens, errors = tokenize(source)
        self.assertEqual(errors, [])
        expected = source.split()
        expected[14:16] = ['ID', 'INT_LIT']
        self.assertEqual([token.kind for token in tokens], expected + ['EOF'])

    def test_lexer_comments_crlf_and_keyword_prefix(self):
        tokens, errors = tokenize('// ignored\r\n  printValue -> x;\r\n')
        self.assertEqual(errors, [])
        self.assertEqual(tokens[0], Token('ID', 'printValue', 2, 3))
        self.assertEqual(tokens[-1], Token('EOF', '', 3, 1))

    def test_external_token_stream_contract(self):
        # A lexer implementation need only construct these shared Token objects.
        tokens = [Token('print', 'print', 1, 1), Token('(', '(', 1, 6),
                  Token('INT_LIT', '7', 1, 7), Token(')', ')', 1, 8),
                  Token(';', ';', 1, 9), Token('EOF', '', 1, 10)]
        expected = parse('print(7);')
        self.assertEqual(Parser(tokens).parse(), expected)
