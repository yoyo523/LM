# Klean Compiler and Virtual Machine

Klean is a statically typed teaching language with `int` and `bool` values,
explicit braces, recursive functions, and left-to-right pipeline assignment.
The implementation follows the Assignment 2a design:

`source -> lexer -> parser/AST -> semantic analysis -> bytecode -> virtual machine`

The project uses only the Python standard library and supports Python 3.10 or
newer.

## Quick start

1. Install Python 3.10 or newer and check `python3 --version`.
2. Clone or download this repository and enter the extracted project directory.
3. No pip packages or compilation step are required; all dependencies are in
   the Python standard library.
4. Run the example:

```bash
python3 -m klean examples/report_examples.kln
```

Expected output:

```text
23
6
21
```

Useful inspection options:

```bash
python3 -m klean examples/report_examples.kln --tokens --no-run
python3 -m klean examples/report_examples.kln --ast --no-run
python3 -m klean examples/report_examples.kln --bytecode --no-run
```

Compilation errors are printed as `file:line:column: message`. Runtime errors
use exit status 2; compilation errors use exit status 1.
Invalid command-line arguments also use status 2.

Execution defaults to at most 1,000,000 VM instructions and 1,000 active
function calls. Increase these positive limits for larger trusted programs:

```bash
python3 -m klean examples/report_examples.kln --max-steps 2000000 --max-frames 2000
```

Exceeding a limit reports a runtime error. Already printed output is retained.
Deep source/AST nesting is rejected with a compilation diagnostic; the exact
threshold depends on the Python interpreter. These limits are not a security
sandbox and do not bound source-file size or total memory.

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

The suite covers lexical positions and errors, parser recovery, precedence,
static type rules, scopes, function calls, recursion, short-circuit logic,
32-bit arithmetic, code generation, and end-to-end execution.

Run the reproducible performance sample with:

```bash
python3 -m examples.benchmark
```

See [validation results](docs/validation.md) for environments, measurements and
remaining checks. The runtime and tests need no third-party packages.
See the [Parser/AST contract](docs/parser_contract.md) for the token interface,
implemented grammar, identifier locations and Member A's integration checklist.
AddressSanitizer, UndefinedBehaviorSanitizer and LeakSanitizer are not applicable
to this pure-Python implementation. Python linting, typing and coverage tools
are optional quality checks, not equivalent substitutes for those sanitizers.

## Language reference

### Types and variables

Klean has signed 32-bit `int` values and `bool` values. Variables require an
explicit type. A variable declared without an initializer must be assigned
before it is read.

```klean
let counter: int = 0;
let ready: bool;
counter + 1 -> counter;
true -> ready;
```

An inner block may shadow a variable from an outer block. Duplicate names in
the same scope are rejected.

### Control flow

Conditions must have type `bool`, and all blocks use braces.

```klean
if (counter > 10) {
    print(counter);
} else {
    print(0);
}

while (counter > 0) {
    counter - 1 -> counter;
}
```

### Functions

Functions are top-level, first-order declarations with typed parameters and a
typed return value. Calls may be recursive.

```klean
fn Fibonacci(n: int) -> int {
    if (n <= 1) { return n; }
    return Fibonacci(n - 1) + Fibonacci(n - 2);
}

print(Fibonacci(8));
```

### Operators

From highest to lowest precedence:

1. Parentheses and calls
2. Unary `-` and `not`
3. `*` and `/`
4. `+` and `-`
5. `<`, `<=`, `>`, `>=`
6. `==`, `!=`
7. `and`
8. `or`

`and` and `or` use short-circuit evaluation. Division truncates towards zero.
Arithmetic outside the signed 32-bit range causes a runtime error.

## Project structure

- `klean/lexer_adapter.py`: token recognition and source positions
- `klean/parser.py`: LL(1) recursive-descent parser with panic recovery
- `klean/ast.py`: tokens, diagnostics, and generic AST nodes
- `klean/semantic.py`: scoped symbol tables and static type checking
- `klean/codegen.py`: AST-to-stack-bytecode translation
- `klean/bytecode.py`: bytecode program representation and formatter
- `klean/vm.py`: checked 32-bit stack virtual machine
- `klean/compiler.py`: complete compiler pipeline API
- `klean/__main__.py`: command-line interface
- `examples/`: runnable Klean programs
- `tests/`: unit and integration tests

## Implementation notes

The compiler collects lexical and syntax diagnostics before semantic analysis.
Code generation only starts after the source passes all checks. The VM uses a
stack for expression values and a separate activation frame for every function
call. Each frame holds nested lexical scopes; functions may also read top-level
variables that are declared before the function. Bytecode jumps implement
`if`, `while`, and short-circuit Boolean operators.

The lexer continues after illegal characters. The parser recovers at semicolons,
closing braces, and statement starts so a single run can report multiple errors.

Uninitialised reads and missing function returns are checked at runtime;
there is no static definite-assignment or all-path return analysis. Arrays,
constants and input statements are not implemented. Their required syntax and
semantics must be confirmed against the group's design and marking rubric.
