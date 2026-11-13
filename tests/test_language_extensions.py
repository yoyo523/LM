"""Regression coverage for arrays, constants, input, and lexical function scope."""
import unittest

from klean.compiler import compile_source
from klean.vm import KleanRuntimeError, execute


class LanguageExtensionTests(unittest.TestCase):
    def run_source(self, source, lines=()):
        compiled = compile_source(source)
        self.assertEqual(compiled.diagnostics, [])
        self.assertIsNotNone(compiled.bytecode)
        output = []
        remaining = iter(lines)

        def read():
            try:
                return next(remaining)
            except StopIteration:
                raise EOFError from None

        execute(compiled.bytecode, output.append, input_reader=read)
        return output

    def test_array_reads_writes_and_boolean_output(self):
        self.assertEqual(self.run_source('''
            let a: int[] = [1, 2, 3]; 9 -> a[1];
            print(a); print(a[0] + a[1]);
            let flags: bool[] = [true, false]; true -> flags[1]; print(flags);
        '''), ['[1, 9, 3]', '10', '[true, true]'])

    def test_array_value_semantics_protect_constants(self):
        self.assertEqual(self.run_source('''
            const original: int[] = [1, 2]; let copy: int[] = original;
            9 -> copy[0]; print(original); print(copy);
            fn change(a: int[]) -> int[] { 7 -> a[0]; return a; }
            print(change(original)); print(original);
        '''), ['[1, 2]', '[9, 2]', '[7, 2]', '[1, 2]'])

    def test_array_return_index_and_equality(self):
        self.assertEqual(self.run_source('''
            fn make() -> bool[] { return [true, false]; }
            print(make()[1]); print([1, 2] == [1, 2]);
            print([1, 2] != [1, 3]); print([7, 8][1]);
            let a: int[]; [4, 5] -> a; print(a[0]);
        '''), ['false', 'true', 'true', '8', '4'])

    def test_array_loop_and_scope(self):
        self.assertEqual(self.run_source('''
            let a: int[] = [2, 4, 6]; let i: int = 0; let sum: int = 0;
            while (i < 3) { sum + a[i] -> sum; i + 1 -> i; }
            if (true) { let a: bool[] = [false]; print(a[0]); }
            print(sum); print(a[2]);
        '''), ['false', '12', '6'])

    def test_const_expression_and_shadowing(self):
        self.assertEqual(self.run_source('''
            const size: int = 2 + 3;
            if (true) { let size: int = 9; 10 -> size; print(size); }
            print(size);
        '''), ['10', '5'])

    def test_const_modification_rejected(self):
        for source in [
            'const x: int = 1; 2 -> x;',
            'const a: int[] = [1]; 2 -> a[0];',
            'const a: int[] = [1]; [2] -> a;',
            'const a: bool = true; fn f() -> int { false -> a; return 0; }',
        ]:
            with self.subTest(source=source):
                result = compile_source(source)
                self.assertIsNone(result.bytecode)
                self.assertTrue(any('Cannot modify constant' in d.message for d in result.diagnostics))

    def test_extension_syntax_errors(self):
        for source in ['const x: int;', 'let a: int[] = [];',
                       'let a: int[] = [1,];', 'print(input(1));',
                       'let a: int[] = [1;', '1 -> a[0;', 'let a: int[][];']:
            with self.subTest(source=source):
                result = compile_source(source)
                self.assertTrue(result.diagnostics)
                self.assertIsNone(result.bytecode)

    def test_array_type_errors(self):
        cases = [
            ('let a: int[] = [true];', 'initialise'),
            ('let a: int[] = [1, true];', 'same type'),
            ('let a: int[] = [[1]];', 'one-dimensional'),
            ('let a: int[] = [1]; true -> a[0];', 'assign'),
            ('let a: int[] = [1]; print(a[false]);', 'index'),
            ('let a: int = 1; print(a[0]);', 'requires an array'),
            ('let a: int = 1; 2 -> a[0];', 'requires an array'),
            ('let a: int[] = [1]; 2 -> a[true];', 'index'),
            ('print([1] + [2]);', 'operand'),
            ('if ([true]) {}', 'condition'),
            ('print([1] == [true]);', 'same type'),
            ('fn f(a: int[]) -> int { return a[0]; } print(f(1));', 'Argument'),
            ('fn f() -> int[] { return [false]; }', 'must return'),
        ]
        for source, fragment in cases:
            with self.subTest(source=source):
                result = compile_source(source)
                self.assertIsNone(result.bytecode)
                self.assertTrue(any(fragment.lower() in d.message.lower() for d in result.diagnostics))

    def test_array_bounds_and_uninitialised(self):
        for source, fragment in [
            ('let a: int[] = [1]; print(a[-1]);', 'out of bounds'),
            ('let a: int[] = [1]; print(a[1]);', 'out of bounds'),
            ('let a: int[] = [1]; 2 -> a[-1];', 'out of bounds'),
            ('let a: int[] = [1]; 2 -> a[1];', 'out of bounds'),
            ('let a: int[]; print(a[0]);', 'uninitialised'),
            ('let a: int[]; 2 -> a[0];', 'uninitialised'),
        ]:
            with self.subTest(source=source):
                with self.assertRaisesRegex(KleanRuntimeError, fragment):
                    self.run_source(source)

    def test_pipeline_value_before_destination_index(self):
        self.assertEqual(self.run_source('''
            let a: int[] = [0, 0];
            input() -> a[input()]; print(a);
        ''', ['9', '1']), ['[0, 9]'])

    def test_input_int32_sign_whitespace_and_leading_zeroes(self):
        for text, expected in [(' -2147483648 ', '-2147483648'),
                               ('+2147483647', '2147483647'),
                               ('-0007', '-7'), ('0' * 5000 + '8', '8')]:
            with self.subTest(text=text[:25]):
                self.assertEqual(self.run_source('print(input());', [text]), [expected])

    def test_input_failures(self):
        for text in ['', 'true', '1.0', '1 2', '++1', '１２', '2147483648',
                     '-2147483649', '9' * 5000]:
            with self.subTest(text=text[:25]):
                with self.assertRaisesRegex(KleanRuntimeError, 'Input'):
                    self.run_source('print(input());', [text])
        with self.assertRaisesRegex(KleanRuntimeError, 'end of file'):
            self.run_source('print(input());')

    def test_input_short_circuit_and_static_type(self):
        self.assertEqual(self.run_source('print(false and (input() == 1));'), ['false'])
        self.assertEqual(self.run_source('const n: int = input(); print(n);', ['4']), ['4'])
        self.assertTrue(compile_source('let x: bool = input();').diagnostics)

    def test_input_name_backward_compatibility(self):
        self.assertEqual(self.run_source('let input: int = 8; print(input); print(input());', ['7']),
                         ['8', '7'])
        self.assertTrue(compile_source('fn input() -> int { return 1; }').diagnostics)

    def test_duplicate_constant_and_parameter_bindings(self):
        for source in ['const x: int = 1; let x: int = 2;',
                       'let x: int; const x: int = 2;',
                       'fn f(x: int, x: int) -> int { return x; }',
                       'fn f() -> int { return 1; } fn f() -> int { return 2; }']:
            with self.subTest(source=source):
                result = compile_source(source)
                self.assertIsNone(result.bytecode)
                self.assertTrue(any('already declared' in d.message for d in result.diagnostics))

    def test_mutual_recursion_and_nested_return(self):
        self.assertEqual(self.run_source('''
            fn even(n: int) -> bool {
                while (true) { if (n == 0) { return true; } return odd(n - 1); }
            }
            fn odd(n: int) -> bool {
                if (n == 0) { return false; } return even(n - 1);
            }
            print(even(8)); print(odd(8));
        '''), ['true', 'false'])

    def test_functions_use_lexical_globals_and_write_globals(self):
        self.assertEqual(self.run_source('''
            let x: int = 1;
            fn increase() -> int { x + 1 -> x; return x; }
            if (true) { let x: bool = false; print(increase()); print(x); }
            print(x);
        '''), ['2', 'false', '2'])
        self.assertTrue(compile_source('fn f() -> int { return later; } let later: int = 1;').diagnostics)

    def test_all_ordered_comparisons(self):
        self.assertEqual(self.run_source('''
            print(1 < 2); print(2 <= 2); print(3 > 2); print(3 >= 3);
            print(2 == 2); print(2 != 3);
        '''), ['true'] * 6)


if __name__ == '__main__':
    unittest.main()
