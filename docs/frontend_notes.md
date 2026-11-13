# Klean syntax frontend notes

This implementation reflects the Assignment 2a design and the documented 2b extensions in [design changes](design_changes.md). The formal EBNF in the local `Assignment 2a.pdf`, pages 3–4, see frontend_review.md for scope and remaining ambiguities.
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
The production scanner is implemented in `klean/lexer_adapter.py`.

Every AST node has `kind`, source `token`, and `fields`. Consumers can dispatch
on `kind`. JSON serialization uses `dataclasses.asdict`.

| Kind | Fields |
| --- | --- |
| Program | items |
| Block | statements |
| Function | name, name_token, type_parameters, parameters, return_type, body |
| Parameter | name, type |
| VarDecl | name, name_token, type, initializer (node or None) |
| ConstDecl | name, name_token, type, initializer (required node) |
| Assign | value, target (identifier string), target_token |
| AssignIndex | value, target, target_token, index |
| If | condition, then, otherwise (block or None) |
| While | condition, body |
| Return, Print | value |
| Binary | operator, left, right |
| Unary | operator, operand |
| Integer | decimal (original digit string) |
| Boolean | value (Python bool) |
| Variable | name |
| Call | name, arguments |
| Array | elements |
| Index | array, index |
| Input | no fields |

Never pass a partial AST to semantic analysis or execution if either lexer or
parser diagnostics are nonempty. Invalid statements are omitted during recovery.
Recovery tracks nested braces and uses semicolons, closing braces and recognizable statement starts;
it is best-effort and can produce cascading errors after malformed blocks.

## Grammar fidelity

Core productions were checked against Assignment 2a pages 3–4. The matching
implemented rules are documented in parser_contract.md. Keywords are case sensitive.
Functions occur only at top level. Braces are mandatory for control flow.
Assignments end in `-> ID ;` or `-> ID [ expression ] ;`; arbitrary expression
statements are not allowed.
Operator precedence from low to high: or, and, equality, relational, additive,
multiplicative, unary, primary. Repeated binary operators associate left.
Relational comparisons cannot chain; equality operators can chain syntactically,
under the current implementation. Grouping overrides precedence. Function arguments are expressions.

Corrections to examples: `If` becomes `if`, `While` becomes `while`, the colon
after `print(counter)` becomes a semicolon, and the typographic dash becomes `-`.
Arrays, constants and integer input are implemented following the approved 2b
extensions. Their final rules are in the language reference and parser contract.

## Responsibilities outside the Parser

Semantic analysis now checks declarations, scopes, operand and argument types,
Boolean conditions, return placement/types and int32 literal ranges.
The VM implements checked arithmetic, recursion and activation records; bytecode
jumps implement short-circuit evaluation. Uninitialised reads and functions
that finish without returning are runtime errors. Constants cannot be modified;
array accesses check runtime bounds, and input is checked as signed int32.
The semantic stage also checks parametric generic bodies and infers call types.
The separate optimiser performs conservative constant folding and dead-code
removal. The VM uses a managed array heap with mark-and-sweep GC and slot limits.
See [advanced features](advanced_features.md) for their contracts and tests.

## Verification and limitations

Tests check precedence/associativity by AST structure, declaration and function
shapes, source positions, error rejection, recovery and token-stream validation.
CLI integration tests verify the report example outputs 23, 6 and 21.
Excessive nesting is reported by the compiler pipeline as a diagnostic.
VM instruction and function-depth budgets bound execution. These are teaching
limits, not a security sandbox or a comprehensive memory limit.
See validation.md for platform evidence and remaining limitations.

See [Parser contract and grammar review](parser_contract.md) for the lexer
interface, exact identifier locations, current grammar and integration checklist.
The frontend algorithms concern expression parsing, AST construction and
traversal, and syntax recovery; it does not concern thread management.
The [2026-11-13 code-review record](frontend_review.md) documents formal EBNF
verification, frontend-only tests and downstream integration risks.
