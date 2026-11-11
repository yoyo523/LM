# Course Learning Notes

These notes record the terminology and implementation model used by the
University of Adelaide course `2650_COMP_2001_2`. They are a study reference,
not assignment content.

## The Course's Main Argument

Computers operate on low-level, hardware-specific instructions that are not
suited to human use. A programming language provides a precise and unambiguous
human-facing notation, while a compiler or interpreter translates that notation
into operations the machine can execute.

The course builds this idea in three layers:

1. Formal language theory defines which strings belong to a language.
2. Automata provide machines that recognise different classes of language.
3. Language processors turn valid source text into executable behaviour.

## Topic Map

### Topics 1-3: Formal Languages

- Alphabets, strings, languages, language operators, and production rules.
- The Chomsky-style hierarchy: regular, context-free, context-sensitive, and
  unrestricted grammars.
- Pumping lemmas and the limits of language classes.

A custom programming language therefore needs explicit lexical and grammatical
rules. Informal examples alone are insufficient.

### Topics 4-6: Recognising Languages

- Finite automata recognise regular languages and can be deterministic or
  non-deterministic.
- Pushdown automata add a stack and correspond to context-free structure.
- Turing machines add an unbounded tape and model general computation,
  including the limits represented by the halting problem.

The implementation connection is direct: finite automata underpin token
recognition, while stack-like processing is needed for nested syntax.

### Topic 7: Compiler And Interpreter Pipeline

The course decomposes translation into lexical analysis, syntax analysis,
semantic analysis, intermediate code, optimisation, and target code.

Translation only works when every phrase has an unambiguous interpretation.
Assembly is presented as an early translation layer: readable mnemonics are
mapped to hardware-specific binary instructions. Higher-level languages repeat
the same idea at a more expressive level.

### Topic 8: Lexical Analysis

The lexical analyser scans source code character by character, groups
characters into lexemes, classifies each lexeme as a token, and passes a token
stream to the syntax analyser. Recognition is performed using automata.

The course identifies seven common token categories:

- identifiers;
- operators;
- keywords;
- constants;
- literals;
- punctuators;
- special characters.

The symbol table records identifiers and supports scope handling. The lexer
should output tokens with their relevant type, while preserving enough source
location information for useful errors.

### Topic 9: Parsing And Semantic Analysis

Parsing checks whether the token stream conforms to the grammar. The course
covers top-down and bottom-up approaches, left recursion, recursive descent,
lookahead, LL(1), FIRST and FOLLOW sets, and parsing tables.

In recursive descent, grammar rules map naturally to functions. For example:

```text
E  -> T E'
E' -> + T E' | epsilon
T  -> id
```

becomes a `parse_E` function that calls `parse_T` and `parse_E_prime`.
`match(expected)` consumes the current token when it is correct and reports a
syntax error otherwise. Epsilon productions become paths that consume nothing.

After syntax is accepted, semantic analysis checks meaning that grammar alone
cannot establish, such as declarations, types, and valid use of identifiers.

### Topic 10: Code Generation And Optimisation

Code generation handles statements and expressions and may produce an
intermediate form such as three-address code. Complex expressions are broken
into simple operations with temporary values. For example:

```text
x = a + b + c
t1 = b + c
x = a + t1
```

The parse tree guides this translation: non-leaf expression nodes can produce
temporary values, and operands must be generated before the operator that uses
them. Control-flow blocks then provide a basis for later optimisation.

## Implications For This Repository

Once the student group supplies its approved language design, the project
should make these stages visible and testable:

```text
characters -> lexemes -> typed tokens -> parse tree / AST
           -> semantic checks -> intermediate form -> execution or target code
```

Error reporting should identify the failed stage. Tests should cover valid and
invalid inputs at the lexer, parser, semantic, and execution/code-generation
levels. Optimisation comes after the unoptimised pipeline is demonstrably
correct.

## Material Reviewed

- The complete Canvas Modules index for Topics 1-10.
- Topic 7.2: The Problem of Translation.
- Topic 8.3: Lexical Analyzer - Detailed.
- Topic 9.8: Parser: Recursive Descent.
- Topic 10.4: Code Generation: Three Address Code.

The remaining concept pages, workshops, and practicals can be incorporated as
the project reaches the corresponding stage.
