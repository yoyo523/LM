# Current validation

The current implementation includes the array/constant/input extensions
documented in [design changes](design_changes.md). Historical test counts and
platform measurements are preserved separately in [validation history](validation_history.md).

## Reproduce

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q klean examples tests scripts
sh scripts/verify_linux.sh
```

The suite includes lexer/parser, semantic, VM, CLI, boundary, extension and sample
tests. Sample tests execute all 18 manifest cases with exact stdin/stdout, exit
status and diagnostic expectations. No test cases are deliberately skipped.

## Verified results (2026-11-13)

| Environment | Result |
| --- | --- |
| macOS 15.1 arm64 / Python 3.12.4, working tree | 86 tests passed; compileall passed |
| Debian 13 aarch64 Docker / Python 3.10.22, read-only source | 86 tests passed; report output correct; benchmark completed |
| Freshly extracted ZIP / macOS Python 3.12.4 | 86 tests passed; standalone examples and all inspection commands passed |
| Freshly extracted ZIP / Linux Python 3.10.22 Docker | 86 tests passed; report output correct; benchmark completed |

The Linux checks used `python:3.10-slim`, image digest
`sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d`.
No packages were installed in the container. This verifies Linux userspace in
Docker, not native hardware installation.

The archive contained 53 files, including the sample expectation JSON and all
required implementation/tests/docs/scripts. Integrity and exclusions were
checked: no `course/`, Git metadata, Python caches, or nested archives. Original
report stdout remains `23`, `6`, `21`. Arrays/constants output is `12`,
`[2, 9, 6]`, `[2, 4, 6]`, `[true, false]`; input `7` produces `14`.

Linux benchmark medians from the extracted archive (five repetitions; compile /
execute milliseconds): 3,000 statements `33.104 / 3.817`, 100-term expression
`0.643 / 0.140`, 10,000 loop iterations `0.085 / 75.536`. Timings exclude startup,
file I/O and terminal output and are observations rather than thresholds.

All current local Markdown links resolve. Current documentation was checked
for private home-directory paths. Old counts and measurements in the history
file are not current totals.

## Limits and remaining official checks

- VM budgets bound instruction count and function depth. They do not bound
  source size, array allocation/copying memory, elapsed time, or waiting for input.
- Compiler nesting thresholds depend on Python. Excessive nesting produces a
  diagnostic; no compiler optimisation is claimed.
- Static definite-assignment and all-path-return analyses are not implemented;
  unavailable/uninitialised reads and missing returns produce runtime errors.
- Arrays are one-dimensional and nonempty. Input is integer-only.
- Native-code sanitizers do not apply to pure Python. Earlier mypy results do not
  validate subsequent extensions; no new lint/type/coverage result is claimed.
- Canvas expandable rubric, exact submission rules, and actual contribution/
  assistance declarations still require user confirmation.
