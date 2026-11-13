# Validation record

## Member B QA completion (2026-11-13)

The current root project contains **66 tests**. The full suite, bytecode
compilation check, report example, benchmark, and Linux verification script all
completed successfully after the final `if`/`else` end-to-end case and parser
delimiter cases were integrated.

Commands run from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q klean examples tests
./scripts/verify_linux.sh
```

| Environment | Result |
| --- | --- |
| macOS 15.1 arm64, Python 3.12.4 | 66 tests passed in 0.746 seconds; `compileall` passed |
| Linux Docker container, Python 3.10.22 | 66 tests passed in 1.725 seconds; report example printed `23`, `6`, `21` |

The Linux command used the official `python:3.10-slim` image at digest
`sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d`.
The source directory is mounted read-only and no packages are installed in the
container. The observed container was Debian 13/glibc 2.41 on aarch64 Docker
Linux; this is a reproducible Linux userspace test, not a claim of native
hardware validation.

The Linux benchmark reports median compile/execute milliseconds over five
repetitions: 3,000 statements `33.790 / 3.489`; a 100-term expression
`0.598 / 0.134`; and 10,000 loop iterations `0.113 / 73.073`. These are
observations, not performance guarantees. See [the QA matrix](qa_matrix.md)
for the case-to-test mapping.

## Frontend code-review follow-up (2026-11-13)

The suite now contains **65 tests**, all passing locally on macOS/Python 3.9.6.
The report example still outputs `23`, `6`, `21`. Seven new tests exercise the
frontend without semantic/VM imports. The formal Assignment 2a EBNF was located
in Downloads and reviewed against the implementation, resolving the missing-
source limitation recorded below. See [frontend review](frontend_review.md).
Earlier counts and Linux/performance measurements below are historical results.

## Parser/AST follow-up (2026-11-12)

After the runtime-limits update, 12 Parser contract/integration tests were added.
The full suite now has **58 tests**, all passing on macOS with Python 3.9.6 and
the Linux `python:3.10-slim` container with Python 3.10.22. The Linux report
example still prints exactly `23`, `6`, `21`.

The added checks cover identifier-token preservation and exact semantic error
locations, JSON serialization, lexer token compatibility, nested-block recovery,
consecutive syntax errors, EOF boundaries, direct Parser recursion handling,
valid nested blocks and combined call/scope/return execution. See
[the Parser checklist](parser_contract.md) for the two external confirmations
still required: a replacement lexer (if any) and the final approved grammar.

The measurements and 46-test results below are the earlier runtime-limits
baseline, retained as historical evidence; performance was not remeasured for
this Parser follow-up.

## Runtime-limits baseline

Recorded on 2026-11-12 for the runtime-limits and validation update based on
commit `2c88e95`. All commands run from the repository root.

## Functional verification

```sh
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
python3 -m examples.benchmark
```

The suite has 46 tests. It covers parser diagnostics, semantic type/name errors,
scope shadowing, runtime errors, int32 bounds, short-circuit side effects,
resource limits and real CLI subprocess execution. The CLI tests check stdout,
stderr and exit status, including missing files and inspection without execution.
The report example produces exactly `23`, `6`, `21` on separate lines.

| Environment | Result |
| --- | --- |
| macOS 26.0.1 arm64, Python 3.9.6 | 46 tests passed; additional compatibility observation, not the documented minimum |
| Linux x86_64 container, Python 3.10.12, glibc 2.35 | 46 tests passed; report example passed |
| Linux container, official `python:3.10-slim` image, Python 3.10.22 | 46 tests passed; report example passed |

Linux was tested using Docker on macOS, with the existing
`ghcr.io/uadelaide/pdc:2026.S2.0` image under x86_64 emulation. This verifies a
Linux userspace, not a native Linux hardware installation. No dependencies were
installed in the container. The source directory was mounted read-only.
The official Python image was also tested successfully without installing any
additional packages (image digest
`sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d`).

Reproduce with an available Python Linux image:

```sh
docker run --rm -v "$PWD:/work:ro" -w /work \
  -e PYTHONDONTWRITEBYTECODE=1 python:3.10-slim \
  python3 -m unittest discover -s tests -v
```

## Stress cases and execution policy

- 3,000 sequential print statements execute successfully.
- A 100-term addition expression executes successfully.
- 2,000 nested parentheses or blocks and a 3,000-term expression produce a
  compilation diagnostic instead of a Python recursion traceback.
- A 5,000-digit out-of-range literal is rejected before integer conversion;
  5,000 leading zeroes on a valid small number are accepted.
- Infinite loops terminate at the instruction budget. Recursive calls terminate
  at the call-depth budget. Boundary tests check exact successful/failed limits.
- Defaults are 1,000,000 instructions and 1,000 active function calls, excluding
  the main frame. Each instruction, including HALT, consumes one step.
- The CLI exposes `--max-steps` and `--max-frames`; the Python `execute()` API
  exposes corresponding keyword arguments. Limits must be positive.

The compiler nesting threshold is implementation-dependent. No total memory,
wall-clock or source-size budget is enforced. This is not a security sandbox.

## Performance sample

`python3 -m examples.benchmark` reports the median of five runs per case.
Compilation and VM execution are timed separately with `time.perf_counter()`.
Program output goes to a no-op callback. Timings exclude interpreter startup,
file I/O and terminal printing. There is no timing assertion in unit tests.

| Case | macOS compile / execute (ms) | Linux x86_64 emulation compile / execute (ms) |
| --- | --- | --- |
| 3,000 statements | 69.181 / 7.338 | 107.138 / 12.189 |
| 100-term expression | 1.229 / 0.277 | 9.737 / 1.187 |
| 10,000 loop iterations | 0.226 / 147.546 | 0.779 / 339.141 |

These are observations from this machine, not performance guarantees or a fair
cross-platform comparison. CPU load, emulation and Python versions differ.

## Remaining checks

- Reconcile the language features with the actual Assignment 2a feedback and
  Assignment 2b rubric. Arrays, constants and input remain unsupported.
- Confirm the group's policies: overflow raises a runtime error, division
  truncates towards zero, and uninitialised reads/missing returns are runtime
  errors. Static definite-assignment and all-path return analysis are absent.
- Dedicated lint, type-check and coverage reports have not been produced in the
  final root checkout. Native-code Sanitizers are not applicable to this
  pure-Python codebase.
- Prepare the final submission archive only after checking the required contents
  and documenting contributions and permitted assistance accurately.
