# Release and packaging guide

Confirm the archive filename and format required by Canvas before submission.
The packaging command uses only Python's standard library.

## 1. Verify the project

Run from the repository root:

```sh
git status --short
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
python3 -m klean examples/features.kln
python3 -m klean examples/errors.kln
```

The report example must print `23`, `6`, `21` on separate lines. The features
example must print `15`, `true`. The errors example intentionally fails with
compilation diagnostics and exit status 1.

## 2. Package only Assignment 2b deliverables

```sh
python3 scripts/package_submission.py ../klean-assignment-2b.zip
```

Use a new destination filename; existing archives are never overwritten.
The archive has a single `klean-assignment-2b/` root containing:

- `README.md`
- `klean/`: Python implementation
- `tests/`: Python regression tests
- `examples/`: Klean samples and Python demonstrations/benchmark
- `docs/`: Markdown language, QA, and release documentation
- `scripts/`: packaging and Linux verification scripts

The explicit folder and file-type selection excludes `course/`, `.git/`,
`__pycache__/`, `.pyc` files, `.DS_Store`, virtual environments, hidden files,
symbolic links, and generated archives. `course/` contains earlier automata
learning exercises, is retained in the development repository, and is not
needed to run or mark the Klean implementation.

## 3. Inspect and extract the archive

```sh
python3 -m zipfile -l ../klean-assignment-2b.zip
python3 -m zipfile -t ../klean-assignment-2b.zip
release_check=$(mktemp -d)
python3 -m zipfile -e ../klean-assignment-2b.zip "$release_check"
cd "$release_check/klean-assignment-2b"
```

Check that no `course/` folder or cache files appear in the archive listing.
Run the tests and examples from this extracted directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m klean examples/report_examples.kln
PYTHONDONTWRITEBYTECODE=1 python3 -m klean examples/features.kln
python3 -m klean examples/report_examples.kln --tokens --no-run
python3 -m klean examples/report_examples.kln --ast --no-run
python3 -m klean examples/report_examples.kln --bytecode --no-run
```

Optional Linux verification requires a running Docker installation:

```sh
sh scripts/verify_linux.sh
```

Upload the archive after the Canvas requirements and submission checklist are
confirmed. If Canvas requires another archive format, package this same
extracted deliverable folder in that format and verify it again.
