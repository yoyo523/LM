# Assignment 2b submission checklist

This is Member C's release checklist. It distinguishes requirements evidenced
in this repository from details that must still be confirmed in Canvas before
submission.

## Marking rubric (25 points)

The rubric supplied to the group assesses five criteria. The detailed
``view longer description`` text is not reproduced here, so final decisions
must still use the Canvas version.

| Criterion | Points | Current evidence | Submission check |
| --- | ---: | --- | --- |
| Basic Functionality | 7 | Variables, expressions, control flow, functions, recursion, typed values, and errors are covered by `tests/test_execution.py`, `tests/test_semantic.py`, and `tests/test_cli.py`. | Re-run the full suite and manually run the examples from a clean release folder. |
| Advanced Functionality | 3 | Recursion, lexical scopes/shadowing, short-circuit Boolean operations, checked 32-bit arithmetic, and execution limits are implemented and tested. | Confirm these are presented as working language features, not merely source code. |
| Basic Compilation Process | 7 | `klean/` provides tokenisation, parsing/AST, semantic analysis, bytecode generation, and VM execution. Tests and CLI inspection flags expose these stages. | Verify a marker can run `--tokens`, `--ast`, `--bytecode`, valid programs, and invalid programs without modifying source code. |
| Advanced Compilation Process | 3 | Parser recovery, recursive calls, activation frames, short-circuit bytecode jumps, scoped lookup, diagnostics, and resource limits have dedicated tests. | Ensure every claimed advanced process has an executable test or a documented example. |
| Documentation & Ease of Use | 5 | README documents setup, commands, language behaviour, limits, project structure, and tests; validation and release documents record evidence. | Remove private paths, verify every command after extracting the archive, and describe final tests clearly. |

### Full-mark evidence checklist

- [ ] All implemented language features can be demonstrated by a sample or an
  automated test.
- [ ] Tokenisation, lexical analysis, syntax analysis, semantic analysis,
  bytecode generation, and execution can each be inspected or tested directly.
- [ ] A marker can write a small Klean program using the README without changing
  the implementation.
- [ ] Advanced features have both a clear language rule and regression coverage.
- [ ] Code comments, README, test command, sample programs, and package layout
  work from a fresh extracted archive.

## Confirm from Canvas before final submission

- [ ] Submission deadline, upload location, and required archive format.
- [ ] Any rubric details hidden behind Canvas's ``view longer description`` and
  any mandatory features beyond the supplied Assignment 2b brief.
- [ ] Whether the marker expects a compiler, interpreter, or either form.
- [ ] Required development/runtime platform and any prohibited dependencies.
- [ ] Current academic-integrity and permitted-assistance requirements.

Do not mark these items complete based only on repository documentation.

## Required deliverables from the Assignment 2b brief

| Required item | Repository evidence | Status |
| --- | --- | --- |
| Source code | `klean/` | Complete |
| Run/compilation instructions | [README](../README.md) | Complete |
| Sample test programs | `examples/` | Complete |
| Syntax and semantic rules | [README](../README.md), [parser contract](parser_contract.md) | Complete |
| Automated tests | `tests/` and the command below | Complete |
| Evidence of expected output | `tests/test_cli.py`, [validation record](validation.md) | Complete |

Run the full suite from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

Run the main example:

```sh
python3 -m klean examples/report_examples.kln
```

Expected output:

```text
23
6
21
```

## Functional release checks

- [ ] The full test command passes in the final release directory.
- [ ] `examples/report_examples.kln` prints `23`, `6`, and `21` on separate lines.
- [ ] `examples/features.kln` prints its documented results.
- [ ] `examples/errors.kln` fails with diagnostics and a non-zero exit code.
- [ ] `--tokens --no-run`, `--ast --no-run`, and `--bytecode --no-run` work on
  the report example.
- [ ] An unreadable source file, lexical error, syntax error, semantic error,
  runtime error, and invalid command-line limit return the documented exit code.
- [ ] The final README matches the submitted command-line behaviour.

## Documentation checks

- [ ] README states the Python version requirement and that no third-party
  packages are needed.
- [ ] README explains installation, execution, testing, inspection options,
  outputs, diagnostics, and execution limits.
- [ ] README's grammar and semantic behaviour match implementation and tests.
- [ ] Language limitations are explicit: arrays, constants, and input statements
  are not implemented; definite assignment and all-path return checks occur at
  runtime rather than statically.
- [ ] Documentation contains no private absolute paths, machine-specific user
  names, secrets, or inaccurate claims about unverified platforms.
- [ ] The final contribution record accurately reflects work actually completed
  by each group member and any permitted assistance.

## Package checks

- [ ] The archive contains `README.md`, `klean/`, `tests/`, `examples/`, `scripts/`, and
  required supporting documentation.
- [ ] The archive excludes `course/` (earlier automata learning exercises),
  `.git/`, `__pycache__/`, `*.pyc`, virtual
  environments, `.env` files, editor settings, and generated output.
- [ ] The archive is extracted into a fresh directory and the functional release
  checks above are rerun there.
- [ ] The final archive name and format match Canvas instructions.

See [the release guide](release_guide.md) for a repeatable packaging procedure.
