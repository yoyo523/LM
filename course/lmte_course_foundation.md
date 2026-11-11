# Language Models, Translation and Execution: Course Foundation

Verified from the logged-in University of Adelaide Canvas course on
17 September 2026.

## Course Identity

- Course code: `2650_COMP_2001_2`
- Title: Language Models, Translation and Execution
- Teaching period: 2026 Semester 2
- Canvas course: `https://learn.adelaide.edu.au/courses/30869`

## Learning Structure

### Module 1: Language Theory

1. Introduction to Language
2. Regular and Context Free Grammars
3. Context Sensitive and Unrestricted Grammar

This module establishes alphabets, strings, languages, production rules, and
grammar classes. These concepts become the formal specification for the custom
language used later in the course.

### Module 2: Automata Theory

4. Finite State Machines
5. Pushdown Automata
6. Turing Machines

This module connects language classes to computational recognisers. Finite
state machines motivate token recognition, while stack-based automata motivate
parsing nested structures.

### Module 3: Language Processing

7. Compilers and Interpreters
8. Token Recognition and Lexical Analysis
9. Parsing and Translation
10. Code Generation and Compiler Optimisation

This module supplies the architecture for the repository: source text flows
through lexical analysis, parsing, semantic processing, and execution or code
generation.

## Major Assessments

### Assignment 1: Automata Proficiency

- Weight: 15%
- Due: 18 September 2026, 23:59
- Submission: PDF
- Scope: regular languages, grammars, FSMs, and pushdown automata
- AI rule: no AI other than self-study

The tasks convert between sentence constraints, production rules, regular
expressions, and finite state machines.

### Assignment 2a: Custom Language Design

- Weight: 10%
- Due: 23 October 2026, 23:59
- Group size: 3-4 students from the same tutorial class
- Deliverable: PDF report, maximum 6 pages
- Expected effort: 4 hours

The group designs a custom programming language, including features, syntax,
idiosyncrasies, target platform, implementation subtasks, algorithms, workload,
responsibilities, timeline, and sample test programs. The rubric allocates two
points each to originality, completeness, planning, testing, and report quality.

### Assignment 2b: Custom Language Implementation

- Weight: 25%
- Due: 13 November 2026, 23:59
- Expected effort: 30 hours

The group implements the language planned in 2a. The submission must include
source code, build/run instructions, sample programs, and a detailed language
reference sufficient for a marker to write or modify a program.

The rubric emphasises:

- basic functionality: 7 points;
- advanced functionality: 3 points;
- tokenisation, lexical analysis, syntax analysis, and code generation: 7 points;
- advanced compilation processes: 3 points;
- documentation and ease of use: 5 points.

## Project Architecture Implied By The Course

The exact language design must come from the student group. Once approved, the
implementation should normally separate these responsibilities:

```text
source -> lexer -> tokens -> parser -> syntax tree
       -> semantic checks -> interpreter or code generator -> result
```

Tests and documentation are first-class deliverables, not finishing touches.
Each pipeline stage should expose observable behaviour that can be demonstrated
with the group's own sample programs.

## Academic Integrity Boundary

For Assignments 2a and 2b, Canvas permits AI-assisted spelling and grammar
checking, rewriting for style or concision, feedback on language and grammar,
and data cleaning. It explicitly says AI must not generate new ideas, answers,
or content. The students remain accountable for every design and implementation
decision.

Accordingly, this repository may support learning, organisation, review, and
verification. Assessed language design, source code, tests, and report content
must be authored by the student group unless teaching staff provide different
written guidance.
