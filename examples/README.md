# Executable examples and expected results

Run from the repository root with Python 3.10+. Every output below ends with a
newline. The machine-readable source of expectations is `manifest.json`.
The normal test command executes all 24 cases through the real CLI, both with
and without optimisation, and checks
stdin, stdout, exit status, and diagnostic fragments:

```sh
python3 -m unittest discover -s tests -v
```

## Successful programs

Use `python3 -m klean examples/FILE.kln`, replacing `FILE` with a name below.

| File | Demonstrates | Stdin | Expected stdout, in line order |
| --- | --- | --- | --- |
| `arithmetic.kln` | Precedence and pipeline assignment | None | `23` |
| `gcd.kln` | Integer division and loop | None | `6` |
| `fibonacci.kln` | Recursive calls and return values | None | `21` |
| `report_examples.kln` | Original combined 2a examples | None | `23`, `6`, `21` |
| `features.kln` | Loop and boolean expression | None | `15`, `true` |
| `arrays_constants.kln` | Array loop, const, copying, checked element write | None | `12`, `[2, 9, 6]`, `[2, 4, 6]`, `[true, false]` |
| `scope.kln` | Lexical globals, updates and different-type shadowing | None | `2`, `false`, `2` |
| `short_circuit.kln` | Skips input/division in dead branches | None | `false`, `true` |
| `input.kln` | Integer input and constant multiplier | `7` followed by newline | `14` |
| `generics.kln` | Type inference, generic scalar/array functions | None | `7`, `[false, false]`, `true` |
| `memory.kln` | Dynamic allocation, length and managed GC | `3` followed by newline | `3`, `[5, 5, 5]`, `true`, `5` |
| `optimization.kln` | Constant folding, branch/loop/post-return removal | None | `20`, `7`, also with `--no-optimize` |

For input, run interactively and enter `7`, or pipe a line:

```sh
printf '7\n' | python3 -m klean examples/input.kln
```

## Intentional failures

Use the same command for each path. These samples are supposed to fail and
produce no stdout. Diagnostic paths and positions depend on the chosen path;
the stable diagnostic fragments below are checked automatically.

| File | Exit | Diagnostic includes |
| --- | ---: | --- |
| `errors.kln` | 1 | `Cannot initialise` (also reports bad condition/undeclared name) |
| `invalid/lexical.kln` | 1 | `Illegal character` |
| `invalid/syntax.kln` | 1 | `Expected` |
| `invalid/constant.kln` | 1 | `Cannot modify constant` |
| `invalid/array_bounds.kln` | 2 | `Array index out of bounds` |
| `invalid/division.kln` | 2 | `Division by zero` |
| `invalid/generic.kln` | 1 | `must have type int` |
| `invalid/heap_limit.kln` | 2 | `Heap slot limit` |

Additional manifest cases run `input.kln` with invalid text, immediate EOF, and
out-of-range input; each produces exit 2 and an input diagnostic.

## Advanced inspection

```sh
python3 -m klean examples/generics.kln --ast --no-run
printf '3\n' | python3 -m klean examples/memory.kln --heap-stats
python3 -m klean examples/optimization.kln --optimization-report --no-run
python3 -m klean examples/optimization.kln --bytecode --no-run --no-optimize
```

`--heap-stats` produces a separate JSON line on stderr after successful execution.
See [advanced features](../docs/advanced_features.md) for limits and semantics.

## Inspecting the compilation pipeline

```sh
python3 -m klean examples/arrays_constants.kln --tokens --no-run
python3 -m klean examples/arrays_constants.kln --ast --no-run
python3 -m klean examples/arrays_constants.kln --bytecode --no-run
python3 -m klean examples/input.kln --bytecode --no-run
```

Inspection compiles and checks types without executing the program or reading
input. `--bytecode` displays the generated stack instructions and function code.
See [language reference](../docs/language_reference.md) before modifying samples.
