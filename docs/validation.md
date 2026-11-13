# Current validation

This record covers generics, dynamic arrays, the VM-owned mark-and-sweep heap,
and the post-semantic optimiser described in [advanced features](advanced_features.md).
Earlier counts, benchmarks and limitations are preserved in
[validation history](validation_history.md).

## Reproduce

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q klean examples tests scripts
sh scripts/verify_linux.sh
```

The suite contains **119 tests**, including generic inference, heap root tracing,
allocation/reclamation, optimiser equivalence, runtime faults/locations and real
CLI inspection. All 24 sample manifest cases execute with optimisation enabled
and disabled; each checks stdin/stdout/exit status/diagnostic expectations.

## Results (2026-11-13)

- macOS 15.1 arm64 / Python 3.12.4: 119 tests passed; compileall passed.
- Debian 13 aarch64 Docker / Python 3.10.22: 119 tests passed with read-only source;
  original report output remains `23`, `6`, `21`.
- Linux benchmark completed; measurements below are observations, not thresholds.

## Clean-package verification

An independently generated ZIP contained 65 required files, including the
managed heap, optimiser, generic/memory/optimisation samples and dedicated tests.
Its integrity and required contents were checked; course exercises, Git data,
cache files and nested archives were absent.

After extraction into a fresh directory, all 119 tests passed on macOS Python
3.12.4 and again in the read-only Linux Python 3.10.22 container. The sample
manifest ran with both optimisation modes. Advanced CLI inspection and heap
statistics also worked from the extracted tree. No development-checkout imports
were required.

Linux used the official `python:3.10-slim` image at digest
`sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d`.
No packages were installed in the container. This is Linux userspace verification
under Docker, not a native-hardware claim.

## Advanced behaviour checked

- The same generic function executes with inferred int and bool types; generic
  arrays, multiple type parameters, recursion and symbolic forwarding work.
  Invalid/inconsistent types are rejected before code generation.
- Dynamic allocation supports runtime and zero lengths. Negative/oversized
  requests and live-object exhaustion cause controlled errors.
- Mark-and-sweep preserves global, operand, function and block roots, including
  values passed while another argument triggers collection. Tests verify dead
  scope/frame reclamation, pressure collection, transient allocation roots,
  header accounting and internal tracing cycles.
- Original array value/constant semantics remain intact. Heap statistics count
  retained objects (including objects awaiting a future collection), allocations,
  collections, reclamation and slots.
- Optimisation reduces bytecode size while retaining original source ASTs.
  Differential tests preserve scope, calls/input side effects, semantic
  diagnostics, runtime arithmetic fault text and positions. Both execution modes
  pass every documented sample.
- `--heap-stats` keeps program stdout intact and reports JSON on stderr;
  `--no-optimize` and `--optimization-report` expose compiler transformations.
- The public package exports now correctly retain the compiler/VM API.

## Performance observations

Median milliseconds over five repetitions in the Linux container:

| Case | Compile | Execute |
| --- | ---: | ---: |
| 3,000 statements | 39.808 | 3.983 |
| 100-term expression | 0.743 | 0.005 |
| 10,000 loop iterations | 0.108 | 79.725 |

Optimisation is enabled; the constant expression is folded, so these numbers
must not be treated as a comparison with older non-optimising baselines.
Startup, file I/O and terminal output are excluded.

## Limits and final administration

- The heap budget counts array elements plus headers, not total Python bytes.
  Compiler/source memory, elapsed time and input waiting are not bounded.
- Compiler nesting thresholds depend on Python. Static definite-assignment and
  all-path-return analyses remain absent; related failures are checked at runtime.
- Type parameters range over scalar int/bool; T[] provides one-dimensional
  array forms. Nested arrays, OOP, concurrency and closures are unsupported.
- Constant folding/dead-code elimination are implemented; loop unrolling and
  domain-specific optimisation are not claimed.
- Earlier mypy results do not validate new features. No new lint/type/coverage
  result is claimed. Native-code sanitizers do not apply to this pure-Python code.
- Exact upload rules and actual contribution/assistance declarations still
  require user confirmation.
