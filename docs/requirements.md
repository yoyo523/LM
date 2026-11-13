# Assignment 2b requirements and evidence

Sources: the Assignment 2b brief, all five LMTE Implementation Rubric expanded
criterion descriptions, and the Assignment 2a feedback supplied in the project
conversation on 2026-11-13. This map records actual evidence and remaining gaps;
it is not a grade prediction.

## Required deliverables

| Supplied brief requirement | Submitted evidence |
| --- | --- |
| Compiler/interpreter source and compilation/run instructions | `klean/`, README quick start; Python standard library only |
| Sample source programs | Independent `examples/*.kln`, `examples/invalid/`, stdin/stdout/exit expectations in `examples/manifest.json` |
| Detailed syntax and semantics enabling bespoke tests | `docs/language_reference.md`, `docs/parser_contract.md` |
| Instructions for running/testing and code overview | README module map, sample guide, normal unittest command, module comments |
| Review of 2a feedback | `docs/design_changes.md`, array/constant/input tests and samples |
| Submission archive | `scripts/package_submission.py`, clean extraction evidence in `docs/validation.md` |

## Basic Functionality (7 points)

The official description names the following eight features. Each has an
implemented path and executable evidence.

| Required feature | Implementation | Example/test |
| --- | --- | --- |
| Variables | Parser VarDecl/Assign; semantic scoped bindings; VM DECLARE/LOAD/STORE | `examples/arithmetic.kln`, declaration/assignment tests |
| Literals | Lexer INT_LIT/boolean tokens; parser Integer/Boolean/Array; semantic type/range checks | Signed-int32, boolean, array-literal and huge-literal tests |
| Arithmetic | Precedence parser, operand type checks, arithmetic bytecode and checked VM operations | Arithmetic sample, division/overflow/execution tests |
| Selection | Parser If; bool condition check; conditional jumps and VM execution | Features sample and if/else function test |
| Iteration | Parser While; bool condition check; loop jumps, block scopes | GCD sample, loop and instruction-budget tests |
| Functions | Typed signatures/calls/return checks; function bytecode and activation frames | Fibonacci sample, mutual recursion and nested-return tests |
| Multi-element variables/arrays | Array/Index/AssignIndex; typed arrays; BUILD_ARRAY/LOAD_INDEX/STORE_INDEX | Arrays/constants sample and extension array tests |
| Scope | Semantic scope stack and VM block/function/global lookup | Scope sample, shadowing and lexical-global integration tests |

## Advanced Functionality (3 points)

The official examples include object orientation, encapsulation, polymorphism,
generics, static/dynamic memory allocation, and garbage collection. They are
examples rather than a requirement to implement every item.

Current Klean has no user-level classes/objects, access controls, inheritance,
polymorphic dispatch, generics, explicit allocation/deallocation syntax, or
language/VM-owned garbage collector. Python classes used to build the compiler
do not demonstrate object orientation in Klean.

BUILD_ARRAY and array copying allocate Python lists at runtime; function calls
allocate frames. That is host-backed runtime allocation, not evidence by itself
of a separately implemented memory model or collector. No allocation/reclamation
policy or independent memory-lifecycle tests are claimed.

Recursion, arrays, scope, and short-circuit operations remain useful features,
but must not be presented as automatically satisfying this advanced criterion.
Coverage here is limited and needs an explicit feature decision if targeting
the higher rating bands. Do not claim 3/3 from the current evidence.

## Basic Compilation Process (7 points)

| Required stage | Implementation | How to inspect/test |
| --- | --- | --- |
| Tokenization | `klean/lexer_adapter.py`, Token records | `--tokens --no-run`; exact-kind/position tests |
| Lexical Analysis | Regex-based scanner, keyword recognition, comments and illegal-character diagnostics | Lexer contract tests; invalid lexical sample |
| Syntax Analysis | `klean/parser.py`, AST, panic recovery | `--ast --no-run`; precedence/recovery/EOF tests |
| Code Generation | `klean/codegen.py`, label resolution and stack bytecode | `--bytecode --no-run`; end-to-end VM/sample tests |

Tokenization and lexical analysis are handled by the same lexer, with token
creation and lexical validation exposed through the tests. Source files are
compiled to bytecode before VM execution.

## Advanced Compilation Process (3 points)

The official description assesses the number and complexity of additional
processes, including semantic analysis, optimisation, concurrency/parallelism,
and high-level processes such as closures/domain-specific optimisation.

| Official area | Current evidence | Limitation |
| --- | --- | --- |
| Semantic: type checking | Operator/assignment/array/condition/call/return/const checks in semantic.py | No static definite-assignment or all-path-return analysis |
| Semantic: mathematical errors | Compile-time literal range and operand-type checks; runtime overflow/divide-by-zero guards | Runtime guards are not static mathematical proof or compiler optimisation |
| Semantic: order of instantiation | Declaration-before-use binding; function signatures collected first; runtime unavailable/uninitialised checks | Some failures are runtime rather than compile-time |
| Optimisation | No general optimisation pass | No dead-code elimination, constant-folding pass, or loop unrolling |
| Concurrency/parallelism | None | Single-threaded VM; no language threads |
| Closures/domain-specific optimisation | None | Top-level first-order functions only; no captured lexical environments |

Short-circuit jumps implement required evaluation semantics. They are not a
general dead-code-elimination pass. Activation frames and parser recovery are
engineering evidence but do not automatically establish the additional breadth
listed in this criterion. Semantic analysis provides genuine coverage; a wide
variety of advanced processes has not yet been demonstrated.

## Documentation & Ease of Use (5 points)

| Official requirement | Evidence |
| --- | --- |
| Understand structure/layout | README pipeline and module list; frontend/AST contract |
| Identify language features and implementations | Feature and compilation-stage tables in this document; language reference |
| Run supplied tests with little effort | One standard-library unittest command; sample manifest and guide |
| Modify/write bespoke tests from syntax explanation | Complete language reference and grammar; small independent samples |

Clean extracted-package checks passed for the current implementation. Grades
still depend on marker testing; existing test success is not a score guarantee.

## Remaining actions

- Choose whether to add a substantial advanced language feature and additional
  compiler processes before aiming for the top advanced rating bands. Changes
  need corresponding semantics, tests, and documentation.
- Confirm exact deadline, upload location, archive name/format, and any required
  cover sheet or contribution statement.
- Confirm current permitted-assistance requirements and declare actual work/
  assistance accurately.
- Repackage after further changes and submit the required archive.

The supplied 2b brief accepts a compiler or interpreter. Native RISC-V output
and a new six-page PDF report are not required by the text supplied.
