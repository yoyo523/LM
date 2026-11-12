"""Resource and arithmetic boundaries, including hostile source sizes."""
import unittest

from klean.compiler import compile_source
from klean.vm import KleanRuntimeError, execute


class BoundaryTests(unittest.TestCase):
    def run_source(self, source, **limits):
        result = compile_source(source)
        self.assertEqual(result.diagnostics, [])
        output = []
        execute(result.bytecode, output.append, **limits)
        return output

    def test_many_statements(self):
        self.assertEqual(len(self.run_source("print(1);" * 3000)), 3000)

    def test_long_expression(self):
        self.assertEqual(self.run_source("print(" + "+".join(["1"] * 100) + ");"), ["100"])

    def test_excessive_nesting_is_diagnostic(self):
        for source in ["print(" + "(" * 2000 + "1" + ")" * 2000 + ");",
                       "if (true) {" * 2000 + "}" * 2000,
                       "print(" + "+".join(["1"] * 3000) + ");"]:
            result = compile_source(source)
            self.assertIsNone(result.bytecode)
            self.assertTrue(any("recursion limit" in d.message for d in result.diagnostics))

    def test_huge_literal(self):
        result = compile_source("print(" + "9" * 5000 + ");")
        self.assertIsNone(result.bytecode)
        self.assertIn("32-bit", result.diagnostics[0].message)
        self.assertEqual(self.run_source("print(" + "0" * 5000 + "1);"), ["1"])

    def test_int32_edges(self):
        self.assertEqual(self.run_source("print(-2147483648); print(2147483647);"),
                         ["-2147483648", "2147483647"])
        for expression in ["-2147483648 - 1", "2147483647 * 2", "-(-2147483648)"]:
            with self.subTest(expression=expression):
                with self.assertRaisesRegex(KleanRuntimeError, "overflow"):
                    self.run_source(f"print({expression});")

    def test_short_circuit_side_effects(self):
        source = """
        fn noisy() -> bool { print(99); return true; }
        print(false and noisy()); print(true or noisy());
        print(true and noisy()); print(false or noisy());
        """
        self.assertEqual(self.run_source(source), ["false", "true", "99", "true", "99", "true"])

    def test_call_depth_boundary(self):
        source = "fn f(n: int) -> int { if (n == 0) { return 0; } return f(n-1); } print(f(9));"
        self.assertEqual(self.run_source(source, max_frames=10), ["0"])
        with self.assertRaisesRegex(KleanRuntimeError, "call depth limit"):
            self.run_source(source, max_frames=9)

    def test_step_boundary(self):
        # PUSH, PRINT, HALT: the limit includes the terminating instruction.
        self.assertEqual(self.run_source("print(1);", max_steps=3), ["1"])
        with self.assertRaisesRegex(KleanRuntimeError, "Instruction limit"):
            self.run_source("print(1);", max_steps=2)

    def test_missing_return(self):
        with self.assertRaisesRegex(KleanRuntimeError, "without return"):
            self.run_source("fn f() -> int {} print(f());")
