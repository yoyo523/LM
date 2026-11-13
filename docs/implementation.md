# Implementation notes

## Main stages

The lexer uses regular expressions to recognise tokens. It skips whitespace and
`//` comments and records line/column positions. Illegal characters produce
diagnostics. The parser uses recursive descent, with one method per statement
form and precedence levels for expressions. Syntax recovery skips to a semicolon,
brace or statement keyword so more than one error can be reported.

AST nodes have a kind, a source token and named fields. The semantic analyser
uses a stack of symbol tables for scopes. It checks declarations, operand types,
assignment targets, Boolean conditions, function arguments and return types.
Function signatures are collected first to allow recursive and forward calls.
Any compile error prevents code generation and execution.

The generator translates expressions to stack operations and control flow to
jumps. The VM keeps a value stack and one activation frame per function call.
Each frame has its own block scopes. Integer operations check the signed 32-bit
range; division truncates towards zero.

## Generics

Functions can declare type parameters, for example:

```klean
fn first<T>(items: T[]) -> T { return items[0]; }
```

Calls infer `T` from the arguments. Each type parameter must appear in a
parameter type. A generic body is checked with symbolic types, so `T` alone does
not permit arithmetic or Boolean conditions. The compiler uses type erasure:
the same checked bytecode body handles its int/bool instantiations.

## Arrays and memory

Arrays use value semantics. Reading an array variable makes a copy, so changing
a function parameter or a copy does not change the original array.
`array(length, fill)` allocates an array using a runtime length; `len(a)` returns
its length. Zero length is allowed, while negative lengths are runtime errors.

The VM stores arrays in a managed heap and uses handles to refer to them. Roots
are the operand stack, global bindings and all active function/block scopes.
Mark-and-sweep collection removes objects unreachable from those roots.
Temporary values needed during an allocation are also kept as roots.

Collection runs automatically before an allocation exceeds the heap budget.
`collect()` runs it explicitly and returns the number of objects reclaimed.
An array uses one slot for its header and one per element. Empty arrays still
use a header. The slot budget is not a byte limit on the Python process.
`--heap-stats` reports allocations, collections, reclaimed objects and retained
objects; retained objects may include garbage awaiting the next collection.

## Optimisation

After semantic checking, a separate pass folds valid scalar constant expressions
and removes constant-condition branches, false loops and statements after a
return. Selected blocks keep their scopes. The source AST stays unchanged;
the compiler stores the rewritten tree separately.

The pass does not evaluate input, function calls or allocation at compile time.
Overflow and division-by-zero operations are left for the VM to report. It also
keeps effectful operands: `noisy() and false` still calls `noisy()`, and `x * 0`
still reads `x`. `--no-optimize` disables the pass for comparison.

## Changes from Assignment 2a

Arrays, constants and integer input were added after the 2a feedback. Lowercase
keywords and punctuation in the examples were corrected, and test cases now
have explicit expected results. Generics, dynamic allocation/GC and optimisation
were added during 2b. The backend is a stack VM; RISC-V output was not implemented.

There is no static definite-assignment or all-path-return analysis. The VM
reports uninitialised reads and missing returns at runtime. OOP, concurrency,
closures and loop unrolling are not implemented.
