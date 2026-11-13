# Assignment 2b requirements and evidence

Sources: the Assignment 2b brief and LMTE Implementation Rubric supplied in the
project conversation, and the Assignment 2a feedback supplied on 2026-11-13.
The Canvas expandable criterion descriptions have not been provided. This is an
evidence map, not a predicted grade or a declaration that every hidden criterion
has been met.

## Required deliverables

| Supplied brief requirement | Submitted evidence |
| --- | --- |
| Compiler/interpreter source and compilation/run instructions | `klean/`, README quick start; no native compilation/dependencies required |
| Sample source programs | `examples/*.kln`, `examples/invalid/`, exact expectations in `examples/manifest.json` |
| Detailed syntax and semantic rules enabling a marker to write new programs | `docs/language_reference.md`, `docs/parser_contract.md` |
| How to run and test | README, examples guide, standard-library unittest command |
| Comments and implementation overview | Module docstrings/comments, README pipeline and module map, frontend/QA documentation |
| Review 2a feedback | `docs/design_changes.md` and array/constant/input implementations/tests |
| Required submission files/archive | `scripts/package_submission.py`, clean extraction checks in `docs/release_guide.md` |

## Rubric (25 points)

| Criterion | Points | Evidence to inspect |
| --- | ---: | --- |
| Basic Functionality | 7 | Typed variables/constants, arithmetic/logic, arrays, I/O, branching/iteration; execution, semantic, extension, and sample tests |
| Advanced Functionality | 3 | Recursive/mutually recursive functions, typed array arguments/results, lexical scope/shadowing, short-circuit side effects |
| Basic Compilation Process | 7 | Lexer → parser/AST → semantic analysis → bytecode → VM; `--tokens`, `--ast`, `--bytecode`, CLI success/failure samples |
| Advanced Compilation Process | 3 | Scoped symbol resolution, static type/const validation, control-flow jump generation, activation frames, panic recovery; corresponding regression tests |
| Documentation & Ease of Use | 5 | Quick start, complete language reference, independent examples with expectations, QA matrix, reproducible Linux/release procedures |

These demonstrate candidate high-level features/processes. The official
expanded rubric determines whether they meet the expected breadth. Execution
limits and benchmarks are additional engineering evidence, not substitutes for
language or compilation features.

## Still requiring official confirmation

- Expand each rubric criterion in Canvas and check whether it names additional
  mandatory functionality or compilation processes.
- Confirm final deadline, upload location, archive name/format, and any required
  cover sheet or contribution declaration.
- Confirm current academic-integrity/assistance rules; record actual assistance
  and contributions rather than treating current sole maintenance as sole
  authorship of the original implementation.

The supplied 2b brief explicitly accepts a compiler or interpreter. A Python
compiler producing stack bytecode and executing it in a VM implements that
pipeline. Neither native RISC-V output, extra optimisations, nor a new six-page
PDF report is asserted as mandatory by the text supplied so far.
