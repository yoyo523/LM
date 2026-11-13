# Grammar and AST

The lexer returns tokens with `kind`, original `text`, and one-based `line`
and `column`. Keywords and symbols use their literal spelling as token kinds.
Identifiers use `ID`, integers use `INT_LIT`, and exactly one `EOF` ends
the token list. Whitespace and `//` comments are skipped. CRLF counts as one
newline.

## Grammar

Braces mean repetition and square brackets mean optional syntax unless quoted.

```ebnf
program    = { function | statement }, EOF ;
function   = "fn", ID, [ "<", ID, { ",", ID }, ">" ],
             "(", [ parameter, { ",", parameter } ], ")",
             "->", type, block ;
parameter  = ID, ":", type ;
type       = ( "int" | "bool" | ID ), [ "[", "]" ] ;
block      = "{", { statement }, "}" ;
statement  = "let", ID, ":", type, [ "=", expression ], ";"
           | "const", ID, ":", type, "=", expression, ";"
           | "if", "(", expression, ")", block, [ "else", block ]
           | "while", "(", expression, ")", block
           | "return", expression, ";"
           | "print", "(", expression, ")", ";"
           | expression, "->", ID, [ "[", expression, "]" ], ";" ;
expression = conjunction, { "or", conjunction } ;
conjunction = equality, { "and", equality } ;
equality   = relation, { ( "==" | "!=" ), relation } ;
relation   = sum, [ ( "<" | "<=" | ">" | ">=" ), sum ] ;
sum        = product, { ( "+" | "-" ), product } ;
product    = unary, { ( "*" | "/" ), unary } ;
unary      = ( "-" | "not" ), unary | postfix ;
postfix    = primary, { "[", expression, "]" } ;
primary    = INT_LIT | "true" | "false"
           | ID, [ "(", [ expression, { ",", expression } ], ")" ]
           | "[", expression, { ",", expression }, "]"
           | "(", expression, ")" ;
```

An ID used as a type must be a type parameter declared by that function.
The call `input()` takes no arguments. Calls to `array`, `len` and `collect`
use the normal call syntax and are checked as built-ins.

Functions are top-level only. Braces are mandatory for control flow. Standalone
blocks/call statements, trailing commas, `else if` and chained relational
comparisons are not supported. Binary operators associate left; unary operators
associate right. See [language rules](language_reference.md) for type rules and
operator precedence.

## AST

`Parser(tokens).parse()` returns a Program and a list of diagnostics.
A Node contains `kind`, source `token` and a `fields` dictionary.

| Kind | Main fields |
| --- | --- |
| Program / Block | items / statements |
| Function | name, name_token, type_parameters, parameters, return_type, body |
| Parameter | name, type |
| VarDecl / ConstDecl | name, name_token, type, initializer |
| Assign / AssignIndex | value, target, target_token; index for AssignIndex |
| If / While | condition and blocks |
| Return / Print | value |
| Unary / Binary | operator and operand / left / right |
| Variable / Call | name; arguments for Call |
| Integer / Boolean | decimal / value |
| Array / Index | elements / array and index |
| Input | no fields |

Name tokens locate declaration and assignment errors. Malformed statements may
be omitted during recovery, so a tree with diagnostics must not be executed.
Recovery uses semicolons, braces and statement keywords and may produce extra
errors after badly formed blocks.

Optimisation makes a separate tree and may introduce ScopedBlock nodes to keep
block scope after branch removal. `--ast` displays the original source tree.
