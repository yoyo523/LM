# Assignment 2a to 2b implementation decisions

Assignment 2b permits changes, additions, and removals from the 2a design.
This record identifies the final implemented language and feedback addressed;
it does not replace the original 2a report or change historical contributions.

## Retained design

The implementation retains typed declarations, pipeline assignment, mandatory
braces, strict Boolean conditions, recursive functions, recursive-descent
parsing, a positioned AST, scoped semantic checks, bytecode generation, and a
stack virtual machine. RISC-V generation remains a potential target from the
design, not an implemented backend.

## Feedback addressed with approved extensions

The 2a feedback supplied on 2026-11-13 identified missing arrays, constants,
and input, insufficient test expectations, and incorrectly capitalised syntax
examples. The following implementation additions were approved in the current
maintenance work:

| Feedback | Implemented decision | Evidence |
| --- | --- | --- |
| Arrays absent | `int[]`/`bool[]`, nonempty literals, zero-based indexing, checked indexed assignment, value semantics, typed array parameters/returns | `tests/test_language_extensions.py`, `examples/arrays_constants.kln` |
| Constants absent | `const name: Type = expression;`; assignment to the binding or its array elements is rejected | Extension tests and `examples/invalid/constant.kln` |
| Input absent | `input()` returns one checked signed int32 read from stdin | Extension/CLI sample tests, `examples/input.kln` |
| Expected outputs absent | Separate executable samples and a manifest containing stdin/stdout/exit/diagnostic expectations | `examples/README.md`, `examples/manifest.json`, `tests/test_samples.py` |
| Incorrect example syntax | Lowercase `if`/`while`, semicolon terminators, ASCII minus | Runnable examples and parser rejection tests |

The old 2a sample used `input` as a variable name. That remains valid; only
the function-call spelling `input()` denotes the built-in. User functions
cannot redefine it. New array operations lower to `BUILD_ARRAY`, `LOAD_INDEX`,
and `STORE_INDEX`; input lowers to `INPUT`; constant immutability is enforced
before bytecode generation. See the language reference for exact semantics.

## Clarified behaviour and limitations

Int32 operations trap on overflow and division by zero. Division truncates
towards zero. Uninitialised reads and missing returns are runtime errors.
Arrays are one-dimensional, nonempty values; no resizing operation, slicing,
or length function is provided. Static definite-assignment and all-path-return
analysis are absent. VM instruction/frame limits are implemented; compiler
optimisation is not claimed.

## Planning feedback and final administration

The feedback also requested workload/difficulty estimates in the 2a plan.
That is historical planning information: do not invent estimates or completed
contributions retrospectively. Current maintenance covers the complete project
rather than the former A/B/C task labels. If a contribution or planning statement
is requested at submission, record actual authorship, work, and assistance.

The supplied 2b brief and 25-point rubric are tracked in
[requirements and evidence](requirements.md). Their hidden Canvas descriptions,
deadline, and final upload instructions still require confirmation. The 2a
six-page PDF report limit must not be presented as a new 2b requirement.
