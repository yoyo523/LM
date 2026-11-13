# Generics, managed memory, and compiler optimisation

These features directly address the expanded Advanced Functionality and Advanced
Compilation Process criteria. They extend the language reference and have
dedicated positive, negative, boundary and CLI tests. They are evidence of
implemented features, not a guarantee of a particular mark.

## Parametric generic functions

```klean
fn first<T>(items: T[]) -> T { return items[0]; }
fn filled<T>(count: int, value: T) -> T[] { return array(count, value); }
print(first(filled(3, 7)));
print(filled(2, false));
```

Expected output is `7` then `[false, false]`. A function may declare multiple
type parameters, such as `fn left<T, U>(a: T, b: U) -> T { return a; }`.
Type arguments are inferred from actual arguments; explicit type arguments at
call sites are not supported. Each type parameter must occur in at least one
parameter type. An inferred type parameter is scalar `int` or `bool`; use `T[]`
to accept/return arrays. Passing an array directly to a scalar `T` parameter,
inconsistent inference, duplicate type parameters and unknown types are errors.

A generic function is checked once with symbolic types. An unconstrained `T`
supports values, assignment, equality, printing, array elements and returning;
it does not imply arithmetic or Boolean-condition support. `x + 1` where `x: T`
is rejected even if some call passes an integer. Forwarding symbolic values to
other generic functions and recursive generic calls are supported. Locals can
use the function's declared type parameters.

The parser records Function.type_parameters. Semantic signatures retain symbolic
types; calls unify arguments and substitute the result type. Code generation
uses type erasure: one statically checked bytecode body is shared by concrete
instantiations. This is not monomorphisation or generic syntax implemented only
in Python. Tests in `test_generics.py` exercise int/bool instantiation, arrays,
multi-parameter inference, recursion, errors and copying.

## Dynamic array allocation

`array(length, fill)` allocates an array at runtime. `length` is an `int`
expression and `fill` is a scalar `int` or `bool` (or symbolic `T` in a generic
function). Arguments evaluate once, left-to-right, before allocation. Elements
are initialized to the fill value. Length zero is valid; a negative length is a
runtime error. `len(arrayValue)` returns the number of elements. Empty literal
`[]` remains invalid because it does not identify an element type.

```klean
let count: int = input();
let values: int[] = array(count, 5);
print(len(values));
print(values);
```

With input `3`, this prints `3` then `[5, 5, 5]`. No append/slicing operation or
nested array type is provided. Whole-array replacement and copy semantics remain
unchanged. The function names `input`, `array`, `len` and `collect` are reserved
for built-ins; variables may use those names because variable/function lookup
is separate.

## VM-owned heap and garbage collection

The VM uses `HeapRef` handles for arrays and owns a `ManagedHeap` object table.
The heap's mark-and-sweep collector traces roots in the operand stack, global
bindings and all active call/block scopes; it removes unreachable objects and
updates allocation accounting. Roots needed for an in-progress allocation are
also retained. Backing storage is Python, but object reachability, reclamation,
collection triggering and heap capacity are implemented by Klean's runtime.

Leaving a block or returning from a function makes unused arrays eligible for
reclamation. The collector automatically runs if a new allocation would exceed
the budget, then retries the capacity check. A still-too-large request produces
a controlled runtime error. Large dynamic lengths are checked against the
budget before constructing a backing list.

`collect()` explicitly runs this collector and returns the number of heap
objects reclaimed, not bytes. Counts depend on allocation history and automatic
collections, so they should not be assumed constant. Each array read makes a
copy to preserve value semantics; temporary copies are also collected. A live
constant/global array remains a root. Tests verify roots held by callers,
callee locals, operands and returned values, plus automatic collection, cycles
inside the collector's object graph, stale handles and controlled exhaustion.
Klean itself still does not support nested arrays or user-created cyclic values.

The default budget is 1,000,000 slots. Each element and each array header uses
one slot, so an empty array still consumes one slot. Configure it with:

```sh
printf '3\n' | python3 -m klean examples/memory.kln --max-heap-slots 100 --heap-stats
```

Program stdout is `3`, `[5, 5, 5]`, `true`, `5`. With `--heap-stats`, a separate
JSON line on stderr reports allocations, collections, reclaimed/live objects,
used slots and peak slots. It is not an error diagnostic. The slots are a
logical heap budget, not a byte-accurate cap on total Python process memory.
Input waiting, compiler memory and wall-clock time remain unbounded.

## Optimisation pipeline

The pipeline is source → lexer → parser/AST → semantic checking → optimiser →
bytecode → VM. Optimisation is enabled by default. Lexical, syntax and semantic
errors are checked first, including in code later removed as unreachable.

The optimiser performs:

- Scalar constant folding for valid arithmetic, unary operations and comparisons.
- Safe short-circuit simplification when the left operand is a Boolean literal.
- Removal of statically false loops and unselected constant-condition branches.
- Removal of statements after an unconditional return or a branch whose arms
  both return. Selected blocks retain their scope boundaries.

It does not propagate mutable variable values or eliminate effectful operands.
Faulting arithmetic (overflow or division by zero) stays in the generated code,
preserving runtime failure and source location. For example, `x * 0` still reads
`x`, and `noisy() and false` still calls `noisy()`. Input/allocation/collection
calls are never evaluated at compile time. No loop unrolling is claimed.

```sh
python3 -m klean examples/optimization.kln --bytecode --no-run
python3 -m klean examples/optimization.kln --bytecode --no-run --no-optimize
python3 -m klean examples/optimization.kln --optimization-report --no-run
```

Both execution modes print `20` then `7`; optimised bytecode has fewer
instructions. The JSON optimisation report counts folded expressions,
simplified branches and removed statements. `--ast` continues to show the
original source AST. The Python CompilationResult also exposes `optimized_ast`
and `optimization_stats`; `compile_source(source, optimize=False)` bypasses
the pass. Instruction budgets count the actual generated bytecode, so the same
program can use a different step count when optimisation is disabled.

`test_optimizer.py` compares enabled/disabled output, side effects, fault
messages/locations, scopes and bytecode size. `test_advanced_cli.py` verifies the
public report, budget and inspection commands. The original parser and runtime
tests continue to run in the same suite.

## Scope of the implementation

Klean now demonstrates generics, dynamic memory allocation, VM garbage
collection, semantic analysis and multiple optimisation transformations.
Object orientation, encapsulation, inheritance/polymorphic dispatch,
concurrency, closures and domain-specific optimisation are not implemented.
