# Klean

Klean is a small, statically typed language for Assignment 2b. It uses pipeline
assignment (`expression -> variable;`), explicit braces, and typed functions.

## Run

Python 3.10 or newer is required. There are no third-party dependencies or
separate compilation steps. Open a terminal in the project directory and run:

```sh
python3 -m klean examples/report_examples.kln
```

Expected output:

```text
23
6
21
```

To test integer input:

```sh
printf '7\n' | python3 -m klean examples/input.kln
```

This prints `14`. To run all tests:

```sh
python3 -m unittest discover -s tests -v
```

## Language features

- `int` and `bool` values, typed variables and constants
- Arithmetic, comparisons, Boolean operators and short-circuit evaluation
- `if/else`, `while`, block scope and variable shadowing
- Functions, recursion and inferred generic type parameters
- One-dimensional arrays, indexed assignment and integer input/output
- Dynamic array allocation and a mark-and-sweep garbage collector

A short program:

```klean
const count: int = 3;
let values: int[] = [2, 4, 6];
9 -> values[1];
print(values);
```

Output: `[2, 9, 6]`.

The [language reference](docs/language_reference.md) gives the syntax and rules
for writing programs. The [example list](examples/README.md) includes inputs,
expected outputs and programs that deliberately fail.

## Compiler structure

The pipeline is:

`source -> lexer -> parser/AST -> semantic analysis -> optimisation -> bytecode -> VM`

| File | Purpose |
| --- | --- |
| `klean/lexer_adapter.py` | Tokens, comments and lexical errors |
| `klean/parser.py` | Recursive-descent parser and syntax recovery |
| `klean/ast.py` | Tokens, AST nodes and diagnostics |
| `klean/semantic.py` | Scope, type checks, constants and generic inference |
| `klean/optimizer.py` | Constant folding and dead-code removal |
| `klean/codegen.py`, `bytecode.py` | Stack instructions and jump labels |
| `klean/vm.py` | Instruction execution and function calls |
| `klean/heap.py` | Array allocation and garbage collection |
| `klean/compiler.py`, `__main__.py` | Compiler API and command-line entry point |

See [implementation notes](docs/implementation.md) for the main design choices
and [grammar/AST notes](docs/parser_contract.md) for the parser interface.

These commands inspect a program without running it:

```sh
python3 -m klean examples/report_examples.kln --tokens --no-run
python3 -m klean examples/report_examples.kln --ast --no-run
python3 -m klean examples/report_examples.kln --bytecode --no-run
```

Optimisation is on by default. Compare it using:

```sh
python3 -m klean examples/optimization.kln --bytecode --no-run --no-optimize
python3 -m klean examples/optimization.kln --optimization-report --no-run
```

## Errors and limits

Exit status `0` means success, `1` means a source-file or compilation error,
and `2` means a runtime error or invalid command-line option. Errors go to
stderr. Output printed before a runtime error is kept.

Integers are signed 32-bit values. Overflow, division by zero, invalid array
indices and invalid input cause errors. Uninitialised reads and missing function
returns are checked at runtime.

Defaults are 1,000,000 VM instructions, 1,000 function calls and 1,000,000 heap
slots. Change them with `--max-steps`, `--max-frames` and `--max-heap-slots`.
Use `--heap-stats` to print allocation/collection statistics to stderr.
These limits do not bound total process memory or waiting for input.

Arrays are one-dimensional. Generics range over scalar int/bool types and their
array forms. OOP, threads, closures, slicing and append are not supported.

## Submission files

[Test instructions](docs/testing.md) describe the test suite and Linux check.
To make a clean ZIP, use a new output filename:

```sh
python3 scripts/package_submission.py ../klean-submission.zip
```

The ZIP excludes `course/`, old learning demos, Git data and caches. It includes
the code, tests, sample programs, scripts and five documents in `docs/`.
Development assistance is recorded in [assistance notes](docs/assistance.md).
