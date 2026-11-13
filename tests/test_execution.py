import unittest

from klean.compiler import compile_source
from klean.vm import KleanRuntimeError, execute


def run(source):
    result = compile_source(source)
    if result.diagnostics:
        raise AssertionError(result.diagnostics)
    output = []
    execute(result.bytecode, output.append)
    return output


class ExecutionTests(unittest.TestCase):
    def test_arithmetic_precedence_and_pipeline(self):
        self.assertEqual(
            run("let x: int = 15; let y: int = 4; let r: int; x + y * 2 -> r; print(r);"),
            ["23"],
        )

    def test_loop_gcd(self):
        source = """
        let a: int = 54; let b: int = 24; let temp: int;
        while (b != 0) {
            a - (a / b) * b -> temp;
            b -> a;
            temp -> b;
        }
        print(a);
        """
        self.assertEqual(run(source), ["6"])

    def test_if_else_and_function_call(self):
        source = """
        fn choose(value: int, keep: bool) -> int {
            if (keep) { return value; } else { return 0 - value; }
        }
        print(choose(7, true));
        print(choose(7, false));
        """
        self.assertEqual(run(source), ["7", "-7"])

    def test_recursion(self):
        source = """
        fn fib(n: int) -> int {
            if (n <= 1) { return n; }
            return fib(n - 1) + fib(n - 2);
        }
        print(fib(8));
        """
        self.assertEqual(run(source), ["21"])

    def test_scope_shadowing(self):
        self.assertEqual(
            run("let x: int = 1; if (true) { let x: int = 2; print(x); } print(x);"),
            ["2", "1"],
        )

    def test_short_circuit(self):
        source = "print(false and (1 / 0 == 0)); print(true or (1 / 0 == 0));"
        self.assertEqual(run(source), ["false", "true"])

    def test_division_truncates_towards_zero(self):
        self.assertEqual(run("print(-7 / 3); print(7 / -3);"), ["-2", "-2"])

    def test_uninitialised_variable(self):
        result = compile_source("let x: int; print(x);")
        with self.assertRaisesRegex(KleanRuntimeError, "uninitialised"):
            execute(result.bytecode, lambda _: None)

    def test_division_by_zero_and_overflow(self):
        for source, message in [
            ("print(1 / 0);", "Division by zero"),
            ("print(2147483647 + 1);", "overflow"),
            ("print(-2147483648 / -1);", "overflow"),
        ]:
            with self.subTest(source=source):
                result = compile_source(source)
                self.assertEqual(result.diagnostics, [])
                with self.assertRaisesRegex(KleanRuntimeError, message):
                    execute(result.bytecode, lambda _: None)


if __name__ == "__main__":
    unittest.main()
