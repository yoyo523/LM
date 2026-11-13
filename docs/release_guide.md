# Release and packaging guide

Use this guide only after the group agrees that the implementation and
documentation are ready. Confirm the archive filename and format with Canvas
before creating the final submission.

## 1. Verify the working tree

From the repository root, review changes and run the release checks:

```sh
git status --short
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
python3 -m klean examples/features.kln
python3 -m klean examples/errors.kln
```

The first two example programs must succeed. `errors.kln` is intentionally
invalid and must report diagnostics with a non-zero exit status.

Check the final README against actual command-line behaviour:

```sh
python3 -m klean examples/report_examples.kln --tokens --no-run
python3 -m klean examples/report_examples.kln --ast --no-run
python3 -m klean examples/report_examples.kln --bytecode --no-run
```

## 2. Prepare a clean release folder

Create a new, empty release folder outside the repository so generated files do
not become tracked. Replace `klean-assignment-2b` with the Canvas-required name.
Choose a name that does not already exist; the command below intentionally
stops if it would overwrite an existing folder.

```sh
release_root="../klean-assignment-2b"
mkdir "$release_root"
cp -R README.md klean tests examples docs "$release_root/"
```

Do not include `.git/`, `__pycache__/`, virtual environments, `.env` files,
editor settings, benchmark output, or files unrelated to Assignment 2b.

## 3. Test the release folder

Run the same commands from the copied folder, not from the development checkout:

```sh
cd "$release_root"
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
```

The expected report-example output is:

```text
23
6
21
```

## 4. Create and inspect the archive

Return to the parent directory and use the archive format required by Canvas.
For a zip submission:

```sh
cd ..
zip -r klean-assignment-2b.zip klean-assignment-2b
unzip -l klean-assignment-2b.zip
```

For a tar.gz submission:

```sh
tar -czf klean-assignment-2b.tar.gz klean-assignment-2b
tar -tzf klean-assignment-2b.tar.gz
```

Extract the chosen archive into a separate temporary directory and repeat the
test command one final time. Upload only the required archive after the Canvas
requirements and the checklist have been confirmed.
