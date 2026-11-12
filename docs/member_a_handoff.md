# Member A: Klean syntax front end

This AI-assisted implementation follows the supplied Assignment 2a grammar.
It is not evidence of independently authored student work.
The repository records course restrictions on AI-generated assignment
content; check permitted use before including this implementation in assessed work.

## Run

Requires Python 3.10 or newer; no third-party packages.
Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
```

The second command compiles and executes the program, printing 23, 6 and 21.
Use `--ast --no-run` to inspect the AST. Exit status is 0 on success, 1 for
read or compilation errors, and 2 for runtime errors or invalid CLI arguments.
Diagnostics go to stderr. Semantic analysis, bytecode generation and a stack
VM are now integrated; see README.md for the complete pipeline.

## Integration contract

`Parser(tokens).parse()` returns `ParseResult(program, diagnostics)`.
Every token is `Token(kind, text, line, column)` with one-based positions.
Kinds are `ID`, `INT_LIT`, `EOF`, or the literal lowercase keyword/punctuation
(e.g. `let`, `->`, `(`). Exactly one EOF must terminate the token list.
The reference scanner in `klean/lexer_adapter.py` is replaceable by the lexer
owner's implementation; it is provided only to make the parser runnable now.

Every AST node has `kind`, source `token`, and `fields`. Consumers can dispatch
on `kind`. JSON serialization uses `dataclasses.asdict`.

| Kind | Fields |
| --- | --- |
| Program | items |
| Block | statements |
| Function | name, parameters, return_type, body |
| Parameter | name, type |
| VarDecl | name, type, initializer (node or None) |
| Assign | value, target (identifier string) |
| If | condition, then, otherwise (block or None) |
| While | condition, body |
| Return, Print | value |
| Binary | operator, left, right |
| Unary | operator, operand |
| Integer | decimal (original digit string) |
| Boolean | value (Python bool) |
| Variable | name |
| Call | name, arguments |

Never pass a partial AST to semantic analysis or execution if either lexer or
parser diagnostics are nonempty. Invalid statements are omitted during recovery.
Recovery uses semicolons, closing braces and recognizable statement starts;
it is best-effort and can produce cascading errors after malformed blocks.

## Grammar fidelity

Core productions follow Assignment 2a pages 3–4. Keywords are case sensitive.
Functions occur only at top level. Braces are mandatory for control flow.
Assignments end in `-> ID ;`; arbitrary expression statements are not allowed.
Operator precedence from low to high: or, and, equality, relational, additive,
multiplicative, unary, primary. Repeated binary operators associate left.
Relational comparisons cannot chain; equality operators can chain syntactically,
as in the report. Grouping overrides precedence. Function arguments are expressions.

Corrections to examples: `If` becomes `if`, `While` becomes `while`, the colon
after `print(counter)` becomes a semicolon, and the typographic dash becomes `-`.
Arrays, constants and input have not been added: the feedback requests them,
but the group has not yet supplied their grammar or semantics.

## Responsibilities outside the Parser

Semantic analysis now checks declarations, scopes, operand and argument types,
Boolean conditions, return placement/types and int32 literal ranges.
The VM implements checked arithmetic, recursion and activation records; bytecode
jumps implement short-circuit evaluation. Uninitialised reads and functions
that finish without returning are runtime errors. Constants remain unsupported.

## Verification and limitations

Tests check precedence/associativity by AST structure, declaration and function
shapes, source positions, error rejection, recovery and token-stream validation.
CLI integration tests verify the report example outputs 23, 6 and 21.
Excessive nesting is reported by the compiler pipeline as a diagnostic.
VM instruction and function-depth budgets bound execution. These are teaching
limits, not a security sandbox or a comprehensive memory limit.
See validation.md for platform evidence and remaining limitations.
