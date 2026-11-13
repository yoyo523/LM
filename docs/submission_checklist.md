# Assignment 2b submission checklist

This checklist covers the whole project. It records verified implementation
evidence separately from official submission details that still need confirmation.

## Verified assignment deliverables

- [x] Compiler source, semantic analysis, bytecode generator, and VM in `klean/`.
- [x] Python 3.10+ quick start and standard-library-only dependencies in README.
- [x] Complete [language reference](language_reference.md) and
  [grammar/AST contract](parser_contract.md).
- [x] Independent sample programs with stdin/stdout/error/exit expectations in
  `examples/manifest.json` and [sample guide](../examples/README.md).
- [x] Lexer, parser, semantic, runtime, CLI, boundary and sample regression tests.
- [x] Original report example outputs `23`, `6`, `21`; features output
  `15`, `true`; deliberate error samples return documented failures.
- [x] Token, AST and bytecode inspection without execution or reading input.
- [x] Additional programs verify mutual recursion, lexical globals, shadowing,
  early return, ordered comparisons, and array parameter/result copying.
- [x] [Design-change record](design_changes.md) addresses the supplied 2a
  feedback: arrays, constants, input, test expectations and corrected syntax.
- [x] Array typing, constant writes and input errors have positive and negative
  regression coverage.
- [x] Linux Python 3.10 container verification and reproducible benchmark command.
- [x] Private home-directory paths removed from submitted documentation.
- [x] Earlier test counts/measurements separated into historical validation.
- [x] Clean archive excludes course exercises, Git metadata, caches and output.
- [x] Archive includes implementation, tests, examples/manifest, documents and scripts.
- [x] Extracted archive tests and examples verified; see [validation](validation.md).

## Rubric evidence (25 points)

| Criterion | Points | Evidence |
| --- | ---: | --- |
| Basic Functionality | 7 | Typed variables/constants/arrays, integer input, expressions, branches/loops; execution, semantic and extension tests |
| Advanced Functionality | 3 | Recursive/mutually recursive functions, array parameters/results, lexical scope/shadowing, short-circuit behaviour |
| Basic Compilation Process | 7 | Tokenisation, parser/AST, semantic checks, code generation and VM; inspection commands and independent sample tests |
| Advanced Compilation Process | 3 | Scoped type/const validation, jump generation, call frames, panic recovery; corresponding integration tests |
| Documentation & Ease of Use | 5 | README, language reference, examples with expected results, QA matrix and clean-release instructions |

This is an evidence map, not a score prediction. The expanded official rubric
determines the required breadth of high-level functions/processes. See
[requirements](requirements.md) for the source and remaining uncertainties.

## User confirmation before final upload

- [ ] Check the expandable Canvas rubric descriptions for any additional
  mandatory language features or compilation processes.
- [ ] Confirm the exact deadline, upload location, archive naming/format, and
  any required cover sheet or contribution statement.
- [ ] Confirm current permitted-assistance rules and provide any required
  declaration of actual contributions/assistance. Sole maintenance now does
  not change historical authorship.
- [ ] After any further edits, regenerate and retest the actual final archive.
- [ ] Upload the required archive to Canvas and confirm successful receipt.

The supplied brief accepts a compiler or interpreter; this project compiles
to bytecode and runs it in a VM. The 2a six-page design-report limit is not a
new 2b deliverable requirement in the supplied text.

## Release commands

From the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
python3 -m klean examples/arrays_constants.kln
printf '7\n' | python3 -m klean examples/input.kln
python3 scripts/package_submission.py ../klean-assignment-2b.zip
```

Use a new archive filename if it already exists, and follow the
[release guide](release_guide.md) to inspect, extract, and verify its contents.
