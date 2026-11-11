# Assignment Workflow

Use this workflow to keep the project aligned with the course and its academic
integrity requirements.

## 1. Establish Student-Owned Requirements

Before implementation, the student group must author and approve:

- the language's features, syntax, semantics, and distinctive behaviour;
- the target execution or compilation platform;
- the task breakdown, ownership, timeline, and chosen parsing approach;
- representative valid and invalid programs.

AI may explain concepts or ask review questions, but must not invent these
assessed decisions.

## 2. Turn The Approved Design Into Specifications

Store the group-approved material as explicit project artefacts:

- lexical rules and token definitions;
- grammar or production rules;
- semantic rules and error behaviour;
- examples with expected token, parse, and execution results;
- installation and command-line usage requirements.

Every implemented feature should trace back to one of these approved rules.

## 3. Implement In Course Order

1. Token recognition and lexical analysis.
2. Parsing and syntax analysis.
3. An intermediate representation or abstract syntax tree.
4. Semantic checking and meaningful diagnostics.
5. Interpretation or code generation.
6. Optional optimisation only after correctness is demonstrated.

Keep each stage independently testable. A failed input should report which
stage rejected it and why.

## 4. Verify With Student-Written Tests

For each language feature, include:

- a minimal valid example;
- a realistic combined example;
- lexical, syntax, and semantic failure cases;
- the expected output or diagnostic;
- a regression test when a bug is fixed.

The marker should be able to modify an example or write a simple new program
using only the language reference and README.

## 5. Review Against The Rubric

Assignment 2a prioritises originality, language completeness, planning,
testing, and report quality. Assignment 2b prioritises basic and advanced
functionality, the complete compilation pipeline, documentation, and ease of
testing.

Before submission, verify that setup instructions work from a clean checkout,
all sample programs produce documented results, responsibilities are accurately
recorded, and the submission format matches Canvas.

## 6. AI Boundary

Allowed support includes concept explanations, self-study exercises, feedback
on student-authored work, debugging guidance, spelling and grammar checking,
and rewriting for clarity or concision. Do not use AI to generate language
ideas, assessed answers, implementation content, or report content.
