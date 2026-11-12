# Parser and AST integration contract

## Member A responsibilities

Member A owns recursive-descent expression and statement parsing, operator
precedence and associativity, AST construction/traversal, source locations and
syntax-error recovery. This work does not include thread management.

## Lexer interface

The lexer returns `(list[Token], list[Diagnostic])`. Both dataclasses are defined
in `klean.ast`. A token has `kind`, original `text`, and one-based `line` and
`column`. Whitespace and `//` comments are omitted. CRLF counts as one newline;
columns count Python string characters, not display widths or UTF-8 bytes.

- Identifier kind: `ID`; integer kind: `INT_LIT` (unsigned decimal digits).
- Keywords use their literal lowercase spelling: `let int bool if else while
  fn return print true false and or not`.
- Punctuation/operators use their literal spelling: `-> <= >= == != + - * /
  < > = : ; , ( ) { }`. Multi-character symbols are recognized before prefixes.
- Identifiers match `[a-zA-Z_][a-zA-Z0-9_]*`; keyword prefixes are ordinary
  identifiers. A minus sign is a separate token, not part of an integer token.
- Exactly one `EOF` token terminates the list. Its text is empty and its location
  is immediately after the source. Empty input is a one-token EOF stream.
- Illegal characters generate lexer diagnostics; callers must not execute the
  remaining tokens if lexical errors exist.

The repository's lexer and manually constructed external token streams are
checked in `tests/test_parser_contract.py`. No separate member-provided lexer
has been supplied, so compatibility with an unseen implementation is not claimed.
Any replacement lexer should run the same contract tests before integration.

## AST interface

`Parser(tokens).parse()` returns `ParseResult(program, diagnostics)`. Each Node
has a `kind`, an anchor `token`, and `fields`. Existing string-valued `name` and
`target` fields are retained for semantic analysis and bytecode generation.

| Node | Identifier location |
| --- | --- |
| Function | `fields['name_token']` is the function-name token; anchor remains `fn` |
| VarDecl | `fields['name_token']` is the variable-name token; anchor remains `let` |
| Assign | `fields['target_token']` is the destination token; anchor remains the expression start |
| Parameter, Variable, Call | The anchor token is already the identifier |

New token fields serialize through `dataclasses.asdict()` into JSON objects with
kind/text/line/column. Downstream consumers should access named fields rather
than rely on an exact field count. Semantic name/assignment diagnostics use the
identifier token, falling back to the anchor for older manually built ASTs.

On ordinary syntax errors, malformed statements are omitted and recovery seeks
a semicolon, a closing brace or a recognized statement-start keyword. Recovery
tracks nested braces to avoid exposing a rejected function's body as outer
statements. It is best-effort: missing delimiters are ambiguous, and expression-
started assignments are not used as synchronization boundaries. Recovery does
not promise a complete AST for invalid input.

If the Python recursion limit is reached during parsing, the parser returns an
empty Program with a diagnostic and advances to EOF. The compiler also guards
later recursive AST passes. Never execute a result containing any diagnostics.

## Implemented grammar reviewed against the current code

This description was checked against the formal EBNF in the local
`Assignment 2a.pdf`, pages 3–4, on 2026-11-13. The productions match that design;
this does not establish compliance with a later rubric or revised specification.
See frontend_review.md for the source and review findings.
Braces below denote repetition only when outside quoted terminals; brackets
denote optional syntax.

```ebnf
program    = { function | statement }, EOF ;
function   = "fn", ID, "(", [ parameter, { ",", parameter } ], ")",
             "->", type, block ;
parameter  = ID, ":", type ;
type       = "int" | "bool" ;
block      = "{", { statement }, "}" ;
statement  = "let", ID, ":", type, [ "=", expression ], ";"
           | "if", "(", expression, ")", block, [ "else", block ]
           | "while", "(", expression, ")", block
           | "return", expression, ";"
           | "print", "(", expression, ")", ";"
           | expression, "->", ID, ";" ;
expression = conjunction, { "or", conjunction } ;
conjunction = equality, { "and", equality } ;
equality   = relation, { ( "==" | "!=" ), relation } ;
relation   = sum, [ ( "<" | "<=" | ">" | ">=" ), sum ] ;
sum        = product, { ( "+" | "-" ), product } ;
product    = unary, { ( "*" | "/" ), unary } ;
unary      = ( "-" | "not" ), unary | primary ;
primary    = INT_LIT | "true" | "false"
           | ID, [ "(", [ expression, { ",", expression } ], ")" ]
           | "(", expression, ")" ;
```

Review findings: functions are top-level only; standalone blocks, standalone
call statements, `else if`, trailing commas and chained relational comparisons
are unsupported. Repeated binary operators associate left; unary operators
nest right. Equality chains parse but remain subject to type checking.
`return` placement and Boolean conditions are semantic checks. Braces are
mandatory for `if`, `else` and `while`.

## Review checklist

| Screenshot item | Evidence / status |
| --- | --- |
| Preserve identifier tokens | AST fields and exact-location/JSON tests |
| Lexer token contract | Documented above; repository lexer and manual stream tests pass; external replacement needs confirmation |
| Parser boundary tests | Nested blocks, excessive nesting, complex calls, consecutive errors, malformed function headers and EOF cases |
| Semantic integration | Identifier diagnostics, call argument types, name resolution and compilation gating |
| VM integration | One combined test verifies recursive calls, nested scopes, shadowing, early return and outer-variable preservation |
| Grammar review | Checked against Assignment 2a PDF pages 3–4; later revisions/rubric remain outside this review |
| Algorithm responsibility | Expression parsing, AST traversal and syntax recovery, as defined above |

The existing tests also verify precedence, associativity, error recovery,
functions, integer boundaries and short-circuit execution. Arrays, constants
and input require approved syntax/semantics before they can be added or assessed.
