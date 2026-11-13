# Klean Compiler and Virtual Machine

Klean is a statically typed teaching language with integers, booleans, typed
one-dimensional arrays, constants, integer input, generic/recursive functions,
a managed array heap, garbage collection, and pipeline assignment. It implements
the Assignment 2a design with the extensions
recorded in [design changes](docs/design_changes.md):

`source -> lexer -> parser/AST -> semantic analysis -> optimisation -> bytecode -> virtual machine`

The project uses only the Python standard library and supports Python 3.10 or
newer.

## Quick start

1. Require Python 3.10 or newer.
2. Clone or download this repository and enter its root directory.
3. No pip packages or compilation step are required.
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
sandbox and do not bound source-file size, total process memory, or input waiting.

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
See the [QA test matrix](docs/qa_matrix.md) for lexer/parser, semantic, runtime,
end-to-end and stress cases with their expected results and activation status.
See the [Parser/AST contract](docs/parser_contract.md) for the token interface,
implemented grammar, identifier locations and frontend integration checks.
Use the [submission checklist](docs/submission_checklist.md) and
[release guide](docs/release_guide.md) before packaging the final archive.
AddressSanitizer, UndefinedBehaviorSanitizer and LeakSanitizer are not applicable
to this pure-Python implementation. Python linting, typing and coverage tools
are optional quality checks, not equivalent substitutes for those sanitizers.

## Language reference

Read the [complete language reference](docs/language_reference.md) to write or
modify programs. The [sample guide](examples/README.md) lists independent examples,
required stdin, exact outputs, and intentional errors. The
[requirements map](docs/requirements.md) links the assignment/rubric to evidence.

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

Constants require initialization; arrays use zero-based indexing and value copying:

```klean
const limit: int = 3;
const source: int[] = [2, 4, 6];
let values: int[] = source;
9 -> values[1];
print(values); // [2, 9, 6]
print(source); // [2, 4, 6]
```

Array literals are nonempty and homogeneous; `int[]` and `bool[]` are supported.
Assigning to a constant or its elements is a compile error. Invalid array
indices cause runtime errors.

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

1. Parentheses, calls, and array indexing
2. Unary `-` and `not`
3. `*` and `/`
4. `+` and `-`
5. `<`, `<=`, `>`, `>=`
6. `==`, `!=`
7. `and`
8. `or`

`and` and `or` use short-circuit evaluation. Division truncates towards zero.
Arithmetic outside the signed 32-bit range causes a runtime error.

### Input and samples

`input()` reads one signed int32 from one line of standard input. Invalid input
or EOF causes a runtime error. No prompt is printed. For example:

```sh
printf '7\n' | python3 -m klean examples/input.kln
```

Expected output is `14`. Run `examples/arrays_constants.kln` for arrays and
constants. The normal test command checks all expectations in
`examples/manifest.json`, including stdin and error exit codes.

## Advanced features

Generic functions infer scalar type parameters and support typed array arguments
and results:

```klean
fn filled<T>(n: int, value: T) -> T[] { return array(n, value); }
print(filled(3, 7));
print(filled(2, false));
```

Expected output is `[7, 7, 7]` then `[false, false]`. Generic bodies are checked
parametrically; a `T` does not imply arithmetic or Boolean-condition support.

`array(length, fill)` dynamically allocates an array, `len(a)` gives its length,
and `collect()` runs Klean's VM-owned mark-and-sweep collector. Arrays retain
copy/value semantics. The heap traces operand/global/call/block roots and
automatically collects before a capacity failure. Each array header and element
uses one logical slot; the default budget is 1,000,000 slots:

```sh
printf '3\n' | python3 -m klean examples/memory.kln --max-heap-slots 100 --heap-stats
```

Normal stdout is preserved; `--heap-stats` adds JSON statistics to stderr after
successful execution. Capacity errors use runtime exit status 2.

Constant folding and dead-code removal are enabled after semantic checking.
Compare the actual generated instructions with:

```sh
python3 -m klean examples/optimization.kln --bytecode --no-run
python3 -m klean examples/optimization.kln --bytecode --no-run --no-optimize
python3 -m klean examples/optimization.kln --optimization-report --no-run
```

Both execution modes print `20` then `7`; optimised bytecode is smaller.
`--ast` displays the original source AST. See
[advanced features](docs/advanced_features.md) for syntax, inference restrictions,
heap accounting, GC roots, optimisation safety and corresponding tests.

## Project structure

- `klean/lexer_adapter.py`: token recognition and source positions
- `klean/parser.py`: LL(1) recursive-descent parser with panic recovery
- `klean/ast.py`: tokens, diagnostics, and generic AST nodes
- `klean/semantic.py`: scoped symbol tables and static type checking
- `klean/optimizer.py`: scalar constant folding and scope-preserving dead-code removal
- `klean/codegen.py`: AST-to-stack-bytecode translation
- `klean/bytecode.py`: bytecode program representation and formatter
- `klean/vm.py`: checked 32-bit stack virtual machine
- `klean/heap.py`: managed arrays, root tracing, allocation budget and garbage collector
- `klean/compiler.py`: complete compiler pipeline API
- `klean/__main__.py`: command-line interface
- `examples/`: runnable Klean programs
- `tests/`: unit and integration tests
- `scripts/`: submission packaging and optional Docker Linux verification
- `course/`: earlier automata learning exercises, excluded from the submission
  archive and not required to run Klean

## Implementation notes

The compiler collects lexical and syntax diagnostics before semantic analysis.
Optimisation and code generation only start after the source passes all checks. The VM uses a
stack for expression values and a separate activation frame for every function
call. Each frame holds nested lexical scopes; functions may also read top-level
variables that are declared before the function. Bytecode jumps implement
`if`, `while`, and short-circuit Boolean operators.

The lexer continues after illegal characters. The parser recovers at semicolons,
closing braces, and statement starts so a single run can report multiple errors.

Uninitialised reads and missing function returns are checked at runtime;
there is no static definite-assignment or all-path return analysis. Arrays are
one-dimensional; literals are nonempty, while `array(0, fill)` produces an empty
array. No slicing or append operation is provided; `len()` reports the length.
Input is integer-only. Waiting for input is not bounded by VM instruction limits.
