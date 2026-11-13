# Klean language reference

This describes the submitted implementation. See [design changes](design_changes.md)
for the extensions made after Assignment 2a and [the parser contract](parser_contract.md)
for the complete grammar and AST interface.

## Source text and names

Source files are UTF-8, normally named `.kln`. Spaces, tabs, newlines, and `//`
comments to the end of the line are ignored. Identifiers match
`[a-zA-Z_][a-zA-Z0-9_]*` and are case-sensitive. Keywords are lowercase:

```text
let const int bool if else while fn return print true false and or not
```

`input()` is a built-in call. The name `input` can still be used for a variable
(as in the original 2a example), but a user function cannot be named `input`.
Strings, floating-point literals, multiline comments, and implicit conversions
are not supported.

## Types and declarations

| Type | Values |
| --- | --- |
| `int` | Signed integers from -2147483648 to 2147483647 |
| `bool` | `true` or `false` |
| `int[]` | One-dimensional arrays of integers |
| `bool[]` | One-dimensional arrays of booleans |

```klean
let total: int = 0;
let ready: bool;
true -> ready;
const limit: int = 3;
let values: int[] = [2, 4, 6];
```

Every declaration requires a type. `let` may omit its initializer; reading an
uninitialised value is a runtime error. `const` requires an initializer and
cannot later be assigned to, including through an array index. Its initializer
is evaluated when execution reaches the declaration; it may contain function
calls or `input()`. Constants are not restricted to compile-time expressions.

Duplicate variable/constant/parameter names in one scope are rejected. Inner
blocks may shadow an outer name, including with a different type. An initializer
is evaluated before the new name is introduced, so it may read an outer binding
with the same name. Function parameters and their outermost function-body
declarations share a scope.

## Pipeline assignment and arrays

```klean
total + 1 -> total;
9 -> values[1];
print(values[0]);
print(values); // [2, 9, 6]
```

Assignment targets must already be declared. Scalar and whole-array assignments
require matching types. For an indexed assignment, the value must match the
element type. The value to the left of `->` is evaluated before the destination
index. Indices are `int` expressions and are zero-based. Negative indices and
indices at or beyond the array length cause runtime errors.

Array literals must be nonempty and contain only one element type. Empty and
nested arrays are unsupported. Arrays can be passed to functions, returned,
printed, compared for equality, or assigned as whole values. Reading an array
produces a copy; assignments and function arguments therefore do not introduce
mutable aliases. Mutating a parameter does not mutate the caller's array. The
constant array itself remains immutable even when a mutable copy is changed.
There are no append, slice, or length built-ins. A whole-array assignment may
replace an array with a different-length array of the same element type.

## Operators and evaluation

Highest to lowest precedence:

| Operators | Operand types | Result |
| --- | --- | --- |
| Calls, grouping, indexing: `f(...)`, `(expr)`, `array[index]` | As specified for each construct | Value/element type |
| Unary `-`, `not` | `int`, `bool` respectively | Same type |
| `*`, `/` | `int`, `int` | `int` |
| `+`, `-` | `int`, `int` | `int` |
| `<`, `<=`, `>`, `>=` | `int`, `int` | `bool` |
| `==`, `!=` | Two values of the same type | `bool` |
| `and` | `bool`, `bool` | `bool` |
| `or` | `bool`, `bool` | `bool` |

Repeated binary operators associate left; unary operators associate right.
Relational comparisons cannot chain: use `a < b and b < c`. Equality chains
parse left-to-right but must still satisfy type rules. Array equality compares
length and element values. Ordering arrays is not supported.

Expressions and function arguments evaluate left-to-right. `and` skips its right
operand when the left is false; `or` skips its right operand when the left is
true, including skipping `input()` and function side effects. Division truncates
towards zero, so `-7 / 3` is `-2`. Division by zero and arithmetic overflow cause
runtime errors; integers do not wrap. Out-of-range literals are compile errors.
The negative literal `-2147483648` is accepted.

## Statements and control flow

```klean
if (total < limit) {
    print(total);
} else {
    print(0);
}
while (total < limit) {
    total + 1 -> total;
}
```

Conditions must be `bool`; parentheses and braces are mandatory. A fresh block
scope is entered for each executed block, including each loop iteration.
`else if` is not a separate form; use an `if` inside an `else` block. Statements
are declarations, pipeline assignments, `if`, `while`, `return`, and `print`.
Standalone expression/call statements and standalone blocks are not supported.
To discard a function result, assign it to a declared variable.

## Functions and lexical scope

```klean
fn first(items: int[]) -> int {
    return items[0];
}
print(first([7, 8]));
```

Functions are declared at top level with explicitly typed parameters and return
type. Nested functions, overloading, and first-class functions are unsupported.
Function signatures are collected before bodies are checked: forward calls,
self-recursion, and mutual recursion are supported. Function names form a
separate namespace from variable names. Duplicate function names are rejected.

`return expression;` is valid only inside a function and must match its result
type. It exits immediately, including from a nested branch or loop. Reaching a
function's end without returning is a runtime error; there is no static
all-path-return analysis.

Functions access their parameters/locals and global variables or constants
declared textually before that function declaration. Caller-local variables are
not visible to a called function. Mutable globals may be updated. Top-level
statements execute in source order, so even a statically visible global must
have been created and initialised when a call actually reads it. Unavailable or
uninitialised globals cause runtime errors.

## Input and output

```klean
let number: int = input();
print(number * 2);
```

`input()` takes no arguments and reads one line from standard input, without
printing a prompt. After surrounding whitespace is removed, the entire line must
match `[+-]?[0-9]+` and fit int32. Leading zeroes are allowed. Invalid text,
out-of-range input, read errors, and EOF cause runtime errors. For example:

```sh
printf '7\n' | python3 -m klean examples/input.kln
```

Expected stdout is `14` followed by a newline. `print(expression);` emits one
line. Booleans print lowercase; arrays print as `[2, 4]` or `[true, false]`.

## Diagnostics and limits

Compilation stops before execution when lexer, parser, or semantic diagnostics
exist. Diagnostics include file/line/column. Exit 0 means successful execution
or inspection, exit 1 means file/compilation failure, and exit 2 means runtime
failure or invalid command-line arguments. Output printed before a runtime
failure is retained. See [examples](../examples/README.md) for failure cases.

The default VM limits are 1,000,000 instructions and 1,000 active function calls.
`--max-steps` and `--max-frames` accept positive integers. Excessive compiler
nesting produces a diagnostic. There are no total memory, source-size, or
wall-clock limits, and waiting for `input()` is not bounded by the instruction
budget. Static definite-assignment analysis and optimisation are not implemented.
