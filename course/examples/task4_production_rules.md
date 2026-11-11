# Task 4: FSM to Production Rules

Source: [Canvas Assignment 1, Task 4](https://learn.adelaide.edu.au/courses/30869/assignments/88729).
The original diagram was inspected in the signed-in browser on 18 September 2026.

Represent each diagram state `z_i` by the nonterminal `Zi`. Take the leftmost
state `Z0` as the start symbol. The terminal alphabet is `{a, b, c}`.
The only accepting state is `Z7`.

## Production Rules

```text
Z0 -> aZ2
Z1 -> cZ2
Z2 -> aZ5 | bZ3 | cZ1
Z3 -> bZ2
Z4 -> cZ5
Z5 -> aZ7 | bZ6 | cZ4
Z6 -> bZ5
Z7 -> epsilon
```

Here `epsilon` denotes the empty string, not a literal input symbol.
Every transition `Zi --x--> Zj` contributes the rule `Zi -> xZj`.
`Z7 -> epsilon` permits the derivation to finish at the accepting state.
Without a terminating rule, no derivation would produce a terminal-only word.

## Transition Cross-Check

| State | a | b | c |
| --- | --- | --- | --- |
| Z0 | Z2 | dead | dead |
| Z1 | dead | dead | Z2 |
| Z2 | Z5 | Z3 | Z1 |
| Z3 | dead | Z2 | dead |
| Z4 | dead | dead | Z5 |
| Z5 | Z7 | Z6 | Z4 |
| Z6 | dead | Z5 | dead |
| Z7 | dead | dead | dead |

The problem specifies an implicit dead state for unshown transitions. Those
transitions cannot lead to acceptance, so they need no productions in this
grammar. In particular, no extra input is accepted after reaching Z7.

## Example Derivations

```text
Z0 => aZ2 => aaZ5 => aaaZ7 => aaa

Z0 => aZ2 => abZ3 => abbZ2 => abbaZ5
   => abbacZ4 => abbaccZ5 => abbaccaZ7 => abbacca
```

The main path reads three `a` symbols. Between the first and second, and between
the second and third, the two-step excursions read `bb` or `cc`. An independent
description of the accepted language is `a(bb|cc)*a(bb|cc)*a`.

Examples accepted: `aaa`, `abbaa`, `accaa`, `aabba`, `aacca`, `abbacca`.
Examples rejected: the empty string, `aa`, `aaaa`, `abaa`, `acaa`, `abccbaa`.
The last example has even totals of both `b` and `c`, but it is rejected because
the machine cannot read `c` immediately after taking the `b` branch to Z3.

An equivalent grammar without an epsilon production replaces `Z5 -> aZ7`
with `Z5 -> a` and removes `Z7 -> epsilon`. Either representation works; the
rules above retain a nonterminal for every state in the original diagram.

## Verification

Run `python3 course/examples/verify_task4_productions.py` from the repository
root. It compares these production rules, the transcribed FSM, and the regular
expression for all 29,524 words over `{a,b,c}` of lengths 0 through 9.
