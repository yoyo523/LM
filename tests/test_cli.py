"""Exercise the actual command-line interface using temporary source files."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def invoke(self, source, *options):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.kln"
            path.write_text(source, encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-m", "klean", str(path), *options],
                cwd=ROOT, capture_output=True, text=True, timeout=10,
            )

    def test_report_example(self):
        result = self.invoke((ROOT / "examples/report_examples.kln").read_text())
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (0, "23\n6\n21\n", ""))

    def test_error_exit_codes(self):
        cases = [("print(@);", 1, "Illegal character"),
                 ("print(1)", 1, "Expected"),
                 ("print(missing);", 1, "has not been declared"),
                 ("print(1 / 0);", 2, "Division by zero")]
        for source, code, message in cases:
            with self.subTest(source=source):
                result = self.invoke(source)
                self.assertEqual(result.returncode, code)
                self.assertEqual(result.stdout, "")
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_inspection_does_not_execute(self):
        for option, expected in [("--tokens", "INT_LIT"), ("--ast", '"Program"'),
                                 ("--bytecode", "DIV")]:
            with self.subTest(option=option):
                result = self.invoke("print(1 / 0);", option, "--no-run")
                self.assertEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)
                self.assertEqual(result.stderr, "")

    def test_execution_limits(self):
        cases = [("while (true) {}", "--max-steps", "20", "Instruction limit"),
                 ("fn f() -> int { return f(); } print(f());",
                  "--max-frames", "4", "call depth limit")]
        for source, option, value, message in cases:
            with self.subTest(option=option):
                result = self.invoke(source, option, value)
                self.assertEqual(result.returncode, 2)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_invalid_limit(self):
        result = self.invoke("print(1);", "--max-steps", "0")
        self.assertEqual(result.returncode, 2)
        self.assertIn("positive integer", result.stderr)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-m", "klean", str(Path(directory) / "absent.kln")],
                cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)
