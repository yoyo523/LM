"""Public commands for generic programs, optimisation comparison and heap limits."""
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AdvancedCLITests(unittest.TestCase):
    def invoke(self, example, *options, stdin=''):
        return subprocess.run([sys.executable, '-m', 'klean', 'examples/' + example, *options],
                              cwd=ROOT, input=stdin, text=True, capture_output=True, timeout=10)

    def test_optimization_report_and_original_bytecode(self):
        result = self.invoke('optimization.kln', '--optimization-report', '--no-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        stats = json.loads(result.stdout)
        self.assertGreater(stats['folded_expressions'], 0)
        self.assertGreater(stats['removed_statements'], 0)
        plain = self.invoke('optimization.kln', '--bytecode', '--no-run', '--no-optimize')
        optimized = self.invoke('optimization.kln', '--bytecode', '--no-run')
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertEqual(optimized.returncode, 0, optimized.stderr)
        self.assertGreater(len(plain.stdout.splitlines()), len(optimized.stdout.splitlines()))

    def test_heap_stats_preserve_program_stdout(self):
        result = self.invoke('memory.kln', '--heap-stats', stdin='3\n')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '3\n[5, 5, 5]\ntrue\n5\n')
        stats = json.loads(result.stderr)
        self.assertGreater(stats['allocations'], 0)
        self.assertGreater(stats['collections'], 0)
        self.assertGreater(stats['reclaimed_objects'], 0)

    def test_heap_budget_failure_and_invalid_option(self):
        result = self.invoke('arrays_constants.kln', '--max-heap-slots', '2')
        self.assertEqual(result.returncode, 2)
        self.assertIn('Heap slot limit', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        invalid = self.invoke('features.kln', '--max-heap-slots', '0')
        self.assertEqual(invalid.returncode, 2)
        self.assertIn('positive integer', invalid.stderr)

    def test_generic_ast_and_heap_inspection_do_not_execute(self):
        generic = self.invoke('generics.kln', '--ast', '--no-run')
        self.assertEqual(generic.returncode, 0, generic.stderr)
        self.assertIn('type_parameters', generic.stdout)
        memory = self.invoke('memory.kln', '--bytecode', '--no-run')
        self.assertEqual(memory.returncode, 0, memory.stderr)
        for operation in ['INPUT', 'NEW_ARRAY', 'COLLECT', 'ARRAY_LEN']:
            self.assertIn(operation, memory.stdout)
