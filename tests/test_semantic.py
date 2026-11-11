import unittest

from klean.compiler import compile_source


def messages(source):
    return [diagnostic.message for diagnostic in compile_source(source).diagnostics]


class SemanticTests(unittest.TestCase):
    def test_valid_program(self):
        result = compile_source(
            "fn same(x: int) -> int { return x; } "
            "let x: int = same(2); if (x == 2) { print(x); }"
        )
        self.assertEqual(result.diagnostics, [])

    def test_undeclared_and_duplicate_variables(self):
        errors = messages("let x: int; let x: int; 1 -> y;")
        self.assertTrue(any("already declared" in error for error in errors))
        self.assertTrue(any("has not been declared" in error for error in errors))

    def test_type_errors(self):
        errors = messages("let x: int = true; if (1) {} print(true + 2);")
        self.assertEqual(len(errors), 3)
        self.assertTrue(any("initialise" in error for error in errors))
        self.assertTrue(any("condition" in error for error in errors))
        self.assertTrue(any("operand" in error for error in errors))

    def test_function_calls_and_return_types(self):
        source = (
            "fn f(x: int, b: bool) -> int { return b; } "
            "print(f(true)); print(nope(1));"
        )
        errors = messages(source)
        self.assertTrue(any("must return int" in error for error in errors))
        self.assertTrue(any("expects 2 arguments" in error for error in errors))
        self.assertTrue(any("Argument 1 must have type int" in error for error in errors))
        self.assertTrue(any("has not been declared" in error for error in errors))

    def test_scope_and_shadowing(self):
        result = compile_source(
            "let x: int = 1; if (true) { let x: bool = false; print(x); } print(x);"
        )
        self.assertEqual(result.diagnostics, [])

    def test_return_outside_function(self):
        self.assertIn("return may only be used inside a function", messages("return 1;"))

    def test_signed_32_bit_literals(self):
        self.assertEqual(compile_source("print(-2147483648);").diagnostics, [])
        self.assertTrue(messages("print(2147483648);"))
        self.assertTrue(messages("print(-2147483649);"))


if __name__ == "__main__":
    unittest.main()
