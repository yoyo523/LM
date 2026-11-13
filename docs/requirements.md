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

| Implemented advanced feature | Implementation | Evidence |
| --- | --- | --- |
| Generics | Parser type-parameter declarations; parametric body checking, argument inference and return substitution; erased bytecode bodies | `test_generics.py`, generic CLI/sample tests, `examples/generics.kln` |
| Dynamic memory allocation | `array(length, fill)`, runtime length checking, VM-owned array handles/table and slot budget | `test_heap.py`, `examples/memory.kln`, heap-limit sample |
| Garbage collection | Klean's mark-and-sweep root traversal, automatic pressure collection, explicit `collect()`, reclamation statistics | Heap roots/cycle/reclamation/budget tests; `--heap-stats` CLI tests |

The heap's backing storage is Python, but logical object ownership, root tracing,
reclamation and capacity are implemented in `klean/heap.py`; this is not a claim
based solely on Python's GC. Generic bodies are checked with symbolic types,
not just separately written int/bool functions. See
[advanced features](advanced_features.md) for exact scope and limitations.

Klean does not implement user classes, access controls, inheritance/polymorphic
dispatch, or static/manual allocation syntax. No score is guaranteed; the
implemented features should be evaluated for breadth and correctness.

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

| Official area | Implemented evidence | Limitation |
| --- | --- | --- |
| Semantic analysis | Scoped declarations, type/const/array/call/return checks; generic inference and parametric checking | No static definite-assignment or all-path-return analysis |
| Mathematical errors | Literal ranges/operand types checked statically; checked runtime arithmetic | Runtime checks are not a static proof of arithmetic safety |
| Instantiation order | Declaration-before-use resolution; signatures collected before bodies; runtime initialisation checks | Some initialisation failures are runtime |
| Optimisation: constant folding | Valid pure scalar arithmetic/unary/comparison expressions folded after semantic checking | Faulting arithmetic and effectful operands preserved |
| Optimisation: dead-code elimination | Constant-condition branch/false-loop removal; post-return unreachable statements removed while preserving scopes | No loop unrolling or general data-flow analysis |
| Concurrency/closures/domain-specific optimisation | Not implemented | Single-threaded, first-order functions |

`test_optimizer.py` compares enabled/disabled results, effects, faults/locations,
scopes and instruction counts. All 24 sample cases also run with optimisation
enabled and disabled. `--no-optimize`, `--bytecode` and
`--optimization-report` expose the actual transformation for marker inspection.
Short-circuit simplification is distinguished from the separate branch and
unreachable-code passes.

Semantic analysis and multiple optimisations now provide evidence in this
criterion. The number and complexity of these processes remain a marking decision.

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

- Review the implemented generics, managed allocation/GC and optimisation
  examples against the expanded rubric; remaining unsupported features are
  recorded explicitly rather than claimed as implemented.
- Confirm exact deadline, upload location, archive name/format, and any required
  cover sheet or contribution statement.
- Confirm current permitted-assistance requirements and declare actual work/
  assistance accurately.
- Repackage after further changes and submit the required archive.

The supplied 2b brief accepts a compiler or interpreter. Native RISC-V output
and a new six-page PDF report are not required by the text supplied.
