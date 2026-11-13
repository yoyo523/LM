"""Parametric function checking, inference, and execution at distinct types."""
import unittest

from klean.compiler import compile_source
from klean.vm import execute


class GenericTests(unittest.TestCase):
    def run_source(self, source):
        result = compile_source(source)
        self.assertEqual(result.diagnostics, [])
        output = []
        execute(result.bytecode, output.append)
        return output

    def test_identity_at_two_types(self):
        self.assertEqual(self.run_source('''
            fn identity<T>(value: T) -> T { return value; }
            print(identity(7)); print(identity(true));
        '''), ['7', 'true'])

    def test_type_variable_arrays_locals_and_return(self):
        self.assertEqual(self.run_source('''
            fn first<T>(a: T[]) -> T { return a[0]; }
            fn pair<T>(a: T, b: T) -> T[] { let items: T[] = [a, b]; return items; }
            print(first(pair(3, 5))); print(pair(true, false));
        '''), ['3', '[true, false]'])

    def test_recursive_forwarding_and_multiple_type_variables(self):
        self.assertEqual(self.run_source('''
            fn repeat<T>(value: T, count: int) -> T {
                if (count == 0) { return value; } return repeat(value, count - 1);
            }
            fn take_left<T, U>(left: T, right: U) -> T { return repeat(left, 2); }
            print(take_left(8, true)); print(take_left(false, 4));
        '''), ['8', 'false'])

    def test_generic_allocation_and_equality(self):
        self.assertEqual(self.run_source('''
            fn filled<T>(n: int, item: T) -> T[] { return array(n, item); }
            fn same<T>(a: T, b: T) -> bool { return a == b; }
            print(filled(3, false)); print(same(2, 2)); print(same(true, false));
        '''), ['[false, false, false]', 'true', 'false'])

    def test_generic_array_value_semantics(self):
        self.assertEqual(self.run_source('''
            fn replace<T>(a: T[], value: T) -> T[] { value -> a[0]; return a; }
            const original: int[] = [1, 2]; print(replace(original, 9)); print(original);
        '''), ['[9, 2]', '[1, 2]'])

    def test_generic_type_errors_rejected_before_codegen(self):
        cases = [
            'fn f<T>(x: T, y: T) -> T { return x; } print(f(1, true));',
            'fn f<T>(x: T[]) -> T { return x[0]; } print(f(1));',
            'fn f<T>(x: T) -> T { return x; } print(f([1]));',
            'fn f<T>(x: T) -> T { return x + 1; }',
            'fn f<T>(x: T) -> bool { if (x) { return true; } return false; }',
            'fn f<T>(x: T) -> T { return 1; }',
            'fn f<T, T>(x: T) -> T { return x; }',
            'fn f<T>() -> T { return 1; }',
            'fn f<T>(x: T) -> T { return x; } print(f());',
            'fn f<T>(x: T) -> T { return x; } let x: bool = f(3);',
            'fn f<T>(x: T) -> T { return x; } let x: T;',
        ]
        for source in cases:
            with self.subTest(source=source):
                result = compile_source(source)
                self.assertTrue(result.diagnostics)
                self.assertIsNone(result.bytecode)

    def test_generic_parser_recovery_resets_type_context(self):
        result = compile_source('fn bad<T>(x: T -> T {} let x: T; print(1);')
        self.assertTrue(result.diagnostics)
        self.assertIsNone(result.bytecode)

    def test_builtin_names_cannot_be_redefined(self):
        for name in ['array', 'len', 'collect']:
            result = compile_source(f'fn {name}() -> int {{ return 1; }}')
            self.assertTrue(any('reserved' in d.message for d in result.diagnostics))
