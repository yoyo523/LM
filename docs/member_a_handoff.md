# Member A: Klean syntax front end

This AI-assisted implementation follows the supplied Assignment 2a grammar.
It is not a complete compiler or evidence of independently authored student
work. The repository records course restrictions on AI-generated assignment
content; check permitted use before including this implementation in assessed work.

## Run

Requires Python 3.9 or newer; no third-party packages.
Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
```

The second command prints JSON AST, not program output. Exit status is 0 for
valid syntax and 1 for read, lexical or syntax errors. Diagnostics go to stderr.
No bytecode generation, type checking or execution is implemented.

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

## Responsibilities remaining outside this module

Semantic analysis must enforce declarations, scopes, operand and argument types,
Boolean conditions, return placement/types, constant rules if adopted, and int32
range rules. Integer tokens remain strings so the semantic stage can correctly
handle the signed minimum and oversized literals.
The runtime must implement short-circuit Boolean evaluation, recursion, activation
records, integer division and the group's chosen overflow/uninitialized-read policy.
Parsing `and`/`or` does not by itself implement short-circuit evaluation.

## Verification and limitations

Tests check precedence/associativity by AST structure, declaration and function
shapes, source positions, error rejection, recovery and token-stream validation.
The report examples should eventually output 23, 6 and 21 respectively, but
these runtime outputs are not verified by this parser-only implementation.
Deeply nested input may reach Python's recursion limit; this is a teaching front
end, with no resource-limit hardening. Linux execution has not yet been verified.
