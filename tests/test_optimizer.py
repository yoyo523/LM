"""Differential checks for optimisation, side effects, diagnostics and scopes."""
import unittest

from klean.compiler import compile_source
from klean.vm import KleanRuntimeError, VirtualMachine


class OptimizerTests(unittest.TestCase):
    def compile(self, source, enabled=True):
        result = compile_source(source, optimize=enabled)
        self.assertEqual(result.diagnostics, [])
        return result

    def output(self, result, lines=()):
        output = []
        remaining = iter(lines)
        def read():
            try:
                return next(remaining)
            except StopIteration:
                raise EOFError from None
        vm = VirtualMachine(result.bytecode, output.append, input_reader=read)
        vm.run()
        return output

    def test_constant_folding_reduces_instructions(self):
        source = 'print((2 + 3) * 4); print(-7 / 3); print(not false); print(2 < 3);'
        optimized, plain = self.compile(source), self.compile(source, False)
        self.assertEqual(self.output(optimized), ['20', '-2', 'true', 'true'])
        self.assertEqual(self.output(optimized), self.output(plain))
        self.assertLess(len(optimized.bytecode.main), len(plain.bytecode.main))
        self.assertGreater(optimized.optimization_stats.folded_expressions, 0)
        self.assertIsNone(plain.optimization_stats)
        self.assertEqual(optimized.ast.fields['items'][0].fields['value'].kind, 'Binary')

    def test_false_branches_loops_and_post_return_code_removed(self):
        source = '''
            fn f() -> int { return 7; print(888); }
            if (false) { print(999); } while (false) { print(777); } print(f());
        '''
        optimized, plain = self.compile(source), self.compile(source, False)
        self.assertEqual(self.output(optimized), ['7'])
        self.assertEqual(self.output(optimized), self.output(plain))
        self.assertGreater(optimized.optimization_stats.removed_statements, 0)
        self.assertGreater(optimized.optimization_stats.simplified_branches, 0)
        self.assertLess(len(optimized.bytecode.functions['f'].instructions), len(plain.bytecode.functions['f'].instructions))

    def test_scope_survives_constant_branch_simplification(self):
        source = 'let x: int = 1; if (true) { let x: bool = false; print(x); } print(x);'
        for enabled in [True, False]:
            self.assertEqual(self.output(self.compile(source, enabled)), ['false', '1'])

    def test_both_return_branches_remove_later_statements(self):
        source = '''
            fn f(flag: bool) -> int { if (flag) { return 1; } else { return 2; } print(999); }
            print(f(true)); print(f(false));
        '''
        self.assertEqual(self.output(self.compile(source)), ['1', '2'])
        self.assertGreater(self.compile(source).optimization_stats.removed_statements, 0)

    def test_runtime_faults_and_locations_preserved(self):
        for expression in ['1 / 0', '2147483647 + 1', '-2147483648 / -1', '-(-2147483648)']:
            with self.subTest(expression=expression):
                errors = []
                for enabled in [True, False]:
                    with self.assertRaises(KleanRuntimeError) as caught:
                        self.output(self.compile(f'print({expression});', enabled))
                    errors.append(str(caught.exception))
                self.assertEqual(errors[0], errors[1])

    def test_semantic_errors_in_dead_code_are_not_hidden(self):
        for source in ['if (false) { print(missing); }',
                       'fn f() -> int { return 1; print(true + 1); }']:
            for enabled in [True, False]:
                result = compile_source(source, optimize=enabled)
                self.assertTrue(result.diagnostics)
                self.assertIsNone(result.bytecode)

    def test_input_calls_and_short_circuit_side_effects(self):
        source = '''
            fn noisy() -> bool { print(9); return true; }
            print(false and noisy()); print(true or (input() == 1));
            print(noisy() and false); print(input() + 2 * 3);
        '''
        for enabled in [True, False]:
            self.assertEqual(self.output(self.compile(source, enabled), ['4']),
                             ['false', 'true', '9', 'false', '10'])

    def test_faulting_operand_not_removed_by_algebra(self):
        for enabled in [True, False]:
            with self.assertRaisesRegex(KleanRuntimeError, 'uninitialised'):
                self.output(self.compile('let x: int; print(x * 0);', enabled))

    def test_literal_minimum_and_large_leading_zeroes(self):
        source = 'print(-2147483648); print(' + '0' * 5000 + '2 + 3);'
        self.assertEqual(self.output(self.compile(source)), ['-2147483648', '5'])
