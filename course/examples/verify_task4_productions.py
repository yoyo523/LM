"""Check Task 4 productions against the transcribed diagram and its language."""

from collections import deque
from itertools import product
from pathlib import Path
import re


notes = Path(__file__).with_name("task4_production_rules.md").read_text()
grammar = {}
for line in notes.splitlines():
    match = re.fullmatch(r"(Z\d+) -> (.+)", line)
    if match:
        grammar[match[1]] = ["" if rule.strip() == "epsilon" else rule.strip()
                             for rule in match[2].split("|")]
assert set(grammar) == {f"Z{i}" for i in range(8)}
for alternatives in grammar.values():
    for rhs in alternatives:
        assert re.fullmatch(r"[abc](Z\d+)?", rhs) or rhs == ""

# Transcribed from the original assignment image, including implicit rejection.
transitions = {
    ("Z0", "a"): "Z2",
    ("Z1", "c"): "Z2",
    ("Z2", "a"): "Z5", ("Z2", "b"): "Z3", ("Z2", "c"): "Z1",
    ("Z3", "b"): "Z2",
    ("Z4", "c"): "Z5",
    ("Z5", "a"): "Z7", ("Z5", "b"): "Z6", ("Z5", "c"): "Z4",
    ("Z6", "b"): "Z5",
}


def fsm_accepts(word):
    state = "Z0"
    for symbol in word:
        state = transitions.get((state, symbol))
        if state is None:
            return False
    return state == "Z7"


max_length = 9
pending = deque(["Z0"])
seen = set()
generated = set()
while pending:
    form = pending.popleft()
    if form in seen or len(re.findall(r"[abc]", form)) > max_length:
        continue
    seen.add(form)
    nonterminal = re.search(r"Z\d+", form)
    if nonterminal is None:
        generated.add(form)
        continue
    for rhs in grammar[nonterminal[0]]:
        pending.append(form[:nonterminal.start()] + rhs + form[nonterminal.end():])

pattern = re.compile(r"a(bb|cc)*a(bb|cc)*a")
checked = 0
for length in range(max_length + 1):
    for chars in product("abc", repeat=length):
        word = "".join(chars)
        result = fsm_accepts(word)
        assert result == (word in generated), f"Grammar mismatch: {word!r}"
        assert result == (pattern.fullmatch(word) is not None), word
        checked += 1
print(f"PASS: FSM, production rules and regex agree on {checked:,} strings (lengths 0-9).")
for word in ["aaa", "abbaa", "accaa", "aabba", "aacca", "abbacca",
             "", "aa", "aaaa", "abaa", "acaa", "abccbaa"]:
    print(f"{word!r}: {'accept' if fsm_accepts(word) else 'reject'}")
