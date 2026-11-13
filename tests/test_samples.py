"""Run the documented sample files through the real CLI with exact expectations."""
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SampleTests(unittest.TestCase):
    def test_all_documented_samples(self):
        cases = json.loads((ROOT / 'examples/manifest.json').read_text(encoding='utf-8'))
        for case in cases:
            with self.subTest(file=case['file'], stdin=case.get('stdin', '')):
                result = subprocess.run(
                    [sys.executable, '-m', 'klean', str(ROOT / 'examples' / case['file'])],
                    input=case.get('stdin', ''), text=True, capture_output=True,
                    cwd=ROOT, timeout=10,
                )
                self.assertEqual(result.returncode, case['exit'], result.stderr)
                self.assertEqual(result.stdout, case['stdout'])
                if case['exit'] == 0:
                    self.assertEqual(result.stderr, '')
                else:
                    self.assertIn(case['stderr_contains'], result.stderr)
                    self.assertNotIn('Traceback', result.stderr)

    def test_extension_inspection_does_not_read_input(self):
        for option, fragment in [('--tokens', 'const'), ('--ast', 'ConstDecl'),
                                 ('--bytecode', 'INPUT')]:
            with self.subTest(option=option):
                result = subprocess.run(
                    [sys.executable, '-m', 'klean', 'examples/input.kln', option, '--no-run'],
                    input='', text=True, capture_output=True, cwd=ROOT, timeout=10,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(fragment, result.stdout)
                self.assertEqual(result.stderr, '')
