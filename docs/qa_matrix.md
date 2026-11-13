# QA test matrix

This matrix maps the requested Member B checks to executable tests. All tests
listed as **enabled** run under the standard `unittest` discovery command; no
semantic or interpreter cases remain parked or skipped because those stages are
now implemented.

Run everything from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
python3 -m examples.benchmark
./scripts/verify_linux.sh
```

The Linux verification script requires Docker; Docker is optional for normal
Klean execution and local tests.

## Lexer and parser

| Case | Executable check | Expected result | Status |
| --- | --- | --- | --- |
| Illegal character | `ParserTests.test_source_locations_and_lexical_errors`, CLI error cases | Diagnostic includes the exact line/column; no traceback | Enabled |
| Missing semicolon | `ParserTests.test_missing_semicolon_preserves_next_statement` | One diagnostic; the following `print` statement remains in the AST | Enabled |
| Missing opening/closing parenthesis | `ParserTests.test_bad_syntax` | Syntax diagnostic, clean termination | Enabled |
| Deep valid nesting | `ParserContractTests.test_valid_nested_blocks` | 20 nested blocks compile and print `7` | Enabled |
| Excessive nesting | parser-contract and boundary depth tests | Compilation diagnostic mentioning the recursion limit; no Python traceback | Enabled |
| Long expression | boundary and frontend-review expression tests | 100 terms evaluate to `100`; 3,000 terms fail with a controlled diagnostic | Enabled |
| Error recovery | recovery, block-recovery and consecutive-error tests | Later valid statements survive in source order | Enabled |
| EOF/incomplete constructs | EOF contract, token-prefix and incomplete-construct tests | Every prefix terminates; malformed EOF produces a positioned diagnostic | Enabled |
| Lexer token contract | lexer kinds, maximal symbols, comments/CRLF and external-token tests | Exact token kinds/positions plus one final EOF token | Enabled |

## Semantic analysis

| Case | Executable check | Expected result | Status |
| --- | --- | --- | --- |
| Undeclared name | `SemanticTests.test_undeclared_and_duplicate_variables` | `has not been declared` diagnostic | Enabled |
| Duplicate declaration | same test plus identifier-location contract | Same-scope duplicate diagnostic at the second name | Enabled |
| Scope and shadowing | semantic and execution shadowing tests | Inner declaration is legal and does not replace the outer value | Enabled |
| Type mismatch | `SemanticTests.test_type_errors` | Initializer/operator diagnostics | Enabled |
| Non-boolean condition | `SemanticTests.test_type_errors` | Condition must be `bool` | Enabled |
| Wrong function arguments | `SemanticTests.test_function_calls_and_return_types` | Arity and argument-type diagnostics | Enabled |
| Invalid return | function return-type and return-outside-function tests | Return-type or placement diagnostic | Enabled |
| Int32 literal policy | signed-literal semantic and boundary tests | `-2147483648` and `2147483647` accepted; out-of-range literals rejected | Enabled |

## Runtime and end-to-end

| Case | Executable check | Expected result | Status |
| --- | --- | --- | --- |
| Arithmetic/precedence | `ExecutionTests.test_arithmetic_precedence_and_pipeline` | Prints `23` | Enabled |
| Pipeline assignment | same test and report example | Computed value is stored in the target | Enabled |
| `if`/`else` and function call | `ExecutionTests.test_if_else_and_function_call` | Prints `7`, then `-7` | Enabled |
| `while` | `ExecutionTests.test_loop_gcd` | Prints `6` | Enabled |
| Recursion | Fibonacci and call-depth tests | Fibonacci prints `21`; depth limit fails cleanly | Enabled |
| `and`/`or` short-circuit | execution and side-effect boundary tests | Dead division/side-effect branches are not evaluated | Enabled |
| Division by zero | execution and CLI error tests | Runtime error, CLI exit status 2, no traceback | Enabled |
| Int32 arithmetic policy | overflow and edge tests | In-range edges execute; overflow raises a runtime error | Enabled |
| Missing return/uninitialised read | boundary and execution tests | Controlled runtime error | Enabled |
| Full CLI path | `CLITests.test_report_example` | Exit 0; stdout is exactly `23\n6\n21\n`; stderr is empty | Enabled |

## Stress and performance

| Case | Executable check | Expected result | Status |
| --- | --- | --- | --- |
| 3,000 statements | `BoundaryTests.test_many_statements` | All 3,000 statements execute | Enabled |
| 100-/3,000-term expressions | long-expression/depth tests | 100 terms succeed; excessive depth is diagnosed | Enabled |
| 2,000 nested blocks/parentheses | excessive-nesting test | Controlled compiler diagnostic | Enabled |
| Deep recursion | call-depth boundary | Exact configured frame limit is enforced | Enabled |
| Infinite loop | CLI execution-limit test | Instruction limit stops execution with status 2 | Enabled |
| Timing sample | `python3 -m examples.benchmark` | JSON containing Python/platform and median compile/run milliseconds | Enabled; informational only |

Performance values are observations, not pass/fail thresholds. See
[`validation.md`](validation.md) for the recorded macOS and Linux results.

## Optional quality tools

Native-code ASan, UBSan and LeakSanitizer do not apply to this pure-Python
implementation. The standard-library `compileall` check passed in the current
checkout. Mypy results from Member B's earlier run are recorded separately in
validation.md. `ruff` and `coverage.py` are intentionally not project dependencies.
To evaluate them in an isolated development environment without changing the
runtime dependency set:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install ruff coverage
ruff check klean tests examples
coverage run -m unittest discover -s tests
coverage report -m
```

Add pinned development dependencies only after the group agrees on the project
packaging policy.
