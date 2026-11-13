# Testing

Run from the project root:

```sh
python3 -m unittest discover -s tests -v
```

The suite has 119 tests. It passed on macOS/Python 3.12.4 and in a Debian Linux
Docker container with Python 3.10.22. It also passed after extracting a clean ZIP.

| Test files | What they check |
| --- | --- |
| `test_parser.py`, `test_parser_contract.py`, `test_frontend_review.py` | Tokens, precedence, AST structure, recovery and EOF |
| `test_semantic.py`, `test_language_extensions.py` | Types, declarations, scope, arrays, constants, input and errors |
| `test_execution.py`, `test_boundaries.py` | Execution, recursion, arithmetic faults and resource limits |
| `test_generics.py` | Generic inference, symbolic body checks and invalid calls |
| `test_heap.py` | Allocation, roots, automatic/manual GC and heap exhaustion |
| `test_optimizer.py` | Optimised/unoptimised output, effects, errors and bytecode size |
| `test_cli.py`, `test_advanced_cli.py` | Real command-line behaviour and exit codes |
| `test_samples.py` | All 24 sample cases, with optimisation on and off |

Sample inputs, outputs, exit codes and diagnostic fragments are in
`examples/manifest.json`. See [the example list](../examples/README.md) to run
individual cases. Failure examples are expected to return non-zero status.

The GC tests check roots held in globals, operands, call frames and block scopes.
They also check that dead objects are reclaimed, live arrays survive collection,
and oversized allocations fail before a large backing list is created.
Optimisation tests compare results and error positions with the pass disabled.

For an optional Linux check, with Docker running:

```sh
sh scripts/verify_linux.sh
```

This runs the tests and report example in `python:3.10-slim` with read-only source.
No packages need to be installed in the container.

## Check the submission ZIP

```sh
python3 scripts/package_submission.py ../klean-submission.zip
python3 -m zipfile -t ../klean-submission.zip
check_dir=$(mktemp -d)
python3 -m zipfile -e ../klean-submission.zip "$check_dir"
cd "$check_dir/klean-assignment-2b"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
```

The report example should print `23`, `6`, `21`. Use a new ZIP filename if one
already exists. Check the required upload format and filename before submission.
