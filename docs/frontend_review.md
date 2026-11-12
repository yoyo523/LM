# Klean frontend code review — 2026-11-13

## Scope and source

Reviewed `klean/parser.py`, `klean/ast.py`, `klean/lexer_adapter.py`,
`tests/test_parser.py`, the contract tests and `docs/member_a_handoff.md`.
Baseline: commit `6b27506`, branch `codex/validation-and-runtime-limits`.
This checkout already includes semantic analysis and a VM; the task description
that these are absent refers to an earlier project state. They were not modified.

Formal source: `/Users/yoyo/Downloads/Assignment 2a.pdf`, Group 25,
section 5, pages 3–4; text extracted and both grammar pages visually inspected.
The PDF is not copied into the repository. This review applies to that design,
not to unprovided later amendments or a marking rubric.
Source SHA-256: `a659eee838e0736ed35da985d22c804403b947b50f59f0d7b89af2ef168103ca`.

## Grammar findings

| Formal productions | Parser mapping and result |
| --- | --- |
| Program / FunctionDecl / ParamList | `items`, `function`: top-level functions, optional typed parameter list, explicit return type; matches |
| Block / Statement | `block`, `statement`: braces mandatory, functions excluded inside blocks; matches |
| VarDecl / AssignStmt | Optional initializer; `Expression -> Identifier ;`; matches |
| IfStmt / WhileStmt | Parenthesized condition, mandatory block, optional else block; matches |
| ReturnStmt / OutputStmt | Required expression and delimiter; matches |
| OrExpr through Term | Six precedence levels; relational production allows at most one operator; matches |
| Factor / Primary / CallOrVar / ArgList | Recursive unary operators, grouping, variables/calls and expression arguments; matches |
| Number / Boolean / Identifier | ASCII decimal digits, Boolean keywords and identifier pattern; matches with keyword reservation |

Binary repetition is folded left and unary operators nest right. The EBNF fixes
precedence but does not explicitly state associativity of repetition: left
folding is the documented implementation convention. Keyword reservation is
also implicit rather than explicitly excluded from the Identifier regex.
The report's uppercase `If`/`While`, colon after print and typographic minus in
examples conflict with formal terminals; the parser follows the formal EBNF.
`LET`/`ARROW` in section 6 are illustrative token labels, whereas the adapter
uses literal `let`/`->`. A replacement lexer must map to the documented contract.

No new grammar-production mismatch or concrete parser defect was established
in this review. No language feature was added.

## AST and changes

The earlier fix is present and tested: Function and VarDecl retain `name_token`;
Assign retains `target_token`; original name/target strings remain compatible
with downstream consumers. Parameter, Variable and Call already anchor on their
identifier. The token's line/column survives JSON serialization.

This review adds seven frontend-only tests, covering every precedence level,
associativity, control-flow AST structure, complex call arguments, truncation at
every token boundary, 3,000 declaration nodes and excessive unary/block nesting.
Existing tests cover consecutive errors, recovery scope, EOF details and token
compatibility. Added AST API docstrings and corrected documentation provenance;
parser algorithms and runtime behavior were not changed in this follow-up.

## Integration requirements and risks

- Use the shared Token class and exactly one trailing EOF. Check lexical and
  parser diagnostics before semantic analysis; recovery trees are inspection-only.
- Dispatch on Node.kind and documented fields. Fields are dynamically typed;
  there is no schema-enforced visitor or static AST field validation.
- Use name_token/target_token for identifier diagnostics, not the statement
  anchor. Full source spans and closing-delimiter tokens are not retained.
- Semantic analysis owns scopes, types, declaration validity, call signatures,
  return placement and int32 range checks. Syntax acceptance is not type validity.
- Runtime owns evaluation, frames, short-circuit behavior and execution limits.
  Parser grouping nodes are intentionally omitted; precedence is encoded by shape.
- Panic recovery is best-effort. Missing delimiters can produce cascaded errors;
  expression-started assignments are not synchronization landmarks.
- Python recursion limits apply to parsing and later AST traversal/serialization.
  Deep parsing returns a diagnostic; large flat inputs still consume proportional
  memory. No manual memory release or thread creation/waiting is required.

## Verification

On macOS with Python 3.9.6, both requested commands completed successfully:

```sh
python3 -m unittest discover -s tests -v
python3 -m klean examples/report_examples.kln
```

Result: **65 tests passed**, including the original 16 parser tests and seven new
frontend-only tests. Example stdout is `23`, `6`, `21` on separate lines.
The documented supported baseline remains Python 3.10+. Linux results from
earlier revisions are recorded separately in validation.md and are not presented
as fresh results for this follow-up.
