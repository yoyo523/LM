# QA test matrix

This matrix maps Member B's checks to executable tests in the repository. All
listed tests run with standard `unittest` discovery; no semantic or interpreter
cases are skipped because those stages are implemented.

Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
python3 -m examples.benchmark
./scripts/verify_linux.sh
```

## Lexer and parser

| Case | Executable evidence | Expected result |
| --- | --- | --- |
| Illegal character | `ParserTests.test_source_locations_and_lexical_errors`, CLI error cases | Positioned diagnostic; no traceback |
| Missing delimiter | `ParserTests.test_bad_syntax`, `test_missing_semicolon_preserves_next_statement` | Syntax diagnostic and clean termination |
| Deep nesting | Parser-contract and boundary depth tests | Valid small nesting executes; excessive nesting is diagnosed |
| Long expression | Boundary and frontend-review tests | 100 terms execute; excessive depth is diagnosed |
| Error recovery | Recovery and consecutive-error tests | Later valid statements remain available |
| EOF/incomplete constructs | EOF-contract, token-prefix and incomplete-construct tests | Positioned diagnostic; parser terminates |
| Token contract | Lexer kind/maximal-symbol, comment/CRLF and external-token tests | Exact tokens/positions plus one trailing EOF |

## Semantic analysis

| Case | Executable evidence | Expected result |
| --- | --- | --- |
| Undeclared or duplicate name | `SemanticTests.test_undeclared_and_duplicate_variables` | Diagnostic at the identifier |
| Scope and shadowing | Semantic and execution shadowing tests | Inner declaration is legal; outer value is preserved |
| Type mismatch/non-boolean condition | `SemanticTests.test_type_errors` | Type diagnostic |
| Function arguments and return | `SemanticTests.test_function_calls_and_return_types` | Arity/type/return diagnostic |
| Int32 literals | Signed-literal semantic and boundary tests | Limits accepted; out-of-range literal rejected |

## Runtime and end-to-end execution

| Case | Executable evidence | Expected result |
| --- | --- | --- |
| Arithmetic and pipeline assignment | `ExecutionTests.test_arithmetic_precedence_and_pipeline` | Prints `23` |
| `if`/`else` and call | `ExecutionTests.test_if_else_and_function_call` | Prints `7`, then `-7` |
| Loop and recursion | GCD, Fibonacci and call-depth tests | Correct output or controlled depth failure |
| Short circuit | Execution and boundary short-circuit tests | Dead branches are not evaluated |
| Runtime arithmetic faults | Execution/CLI division and overflow tests | Exit 2; no traceback |
| Full CLI path | `CLITests.test_report_example` | Exit 0; stdout exactly `23\n6\n21\n` |

## Stress, Linux, and quality checks

| Case | Command/test | Expected result |
| --- | --- | --- |
| 3,000 statements | `BoundaryTests.test_many_statements` | Executes successfully |
| Long/deep expressions | Boundary and frontend-review depth tests | Controlled compiler diagnostic at excessive depth |
| Infinite loop/deep recursion | CLI/boundary limit tests | Step/frame limit causes controlled runtime failure |
| Linux verification | `./scripts/verify_linux.sh` | Tests, example and benchmark run in `python:3.10-slim` |
| Bytecode compilation | `python3 -m compileall -q klean examples tests` | Exit 0 |

Native-code ASan, UBSan and LeakSanitizer do not apply to this pure-Python
project. Optional linting/type/coverage tools should be run in an isolated
development environment and must not be presented as runtime dependencies.
