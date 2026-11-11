"""Compare the NFA drawn in Task 3 with the assignment's regular expression."""

from itertools import product
from pathlib import Path
import re
from xml.etree import ElementTree


root = ElementTree.parse(Path(__file__).with_name("task3_nfa.svg")).getroot()
states = {node.attrib["data-state"] for node in root.iter()
          if "data-state" in node.attrib}
initial = {node.attrib["data-state"] for node in root.iter()
           if node.get("data-initial") == "true"}
accepting = {node.attrib["data-state"] for node in root.iter()
             if node.get("data-accepting") == "true"}
assert len(initial) == 1
transitions = {(state, symbol): set() for state in states for symbol in "ab"}
for edge in root.iter():
    if "data-from" not in edge.attrib:
        continue
    source, target = edge.get("data-from"), edge.get("data-to")
    assert source in states and target in states
    label = next(child for child in edge if child.tag.endswith("}text"))
    symbols = edge.get("data-symbols").split(",")
    assert "".join(label.itertext()).replace(" ", "").split(",") == symbols
    for symbol in symbols:
        assert symbol in "ab"
        assert target not in transitions[source, symbol], "Duplicate edge"
        transitions[source, symbol].add(target)


def accepts(word):
    current = initial.copy()
    for symbol in word:
        current = {target for state in current
                   for target in transitions[state, symbol]}
    return bool(current & accepting)


pattern = re.compile(r"(a|b)*a(aa|bb)b")
checked = 0
for length in range(15):
    for chars in product("ab", repeat=length):
        word = "".join(chars)
        expected = pattern.fullmatch(word) is not None
        assert accepts(word) == expected, f"Incorrect result for {word!r}"
        assert expected == word.endswith(("aaab", "abbb")), word
        checked += 1
print(f"PASS: {checked:,} strings of lengths 0-14 match the regular expression.")
print("Accepting suffixes: aaab or abbb. Empty input is rejected.")
for word in ["aaab", "abbb", "baaab", "babbb", "aaaab", "aaababbb",
             "", "a", "aab", "abb", "abab", "aaaba", "abbbb"]:
    print(f"{word!r}: {'accept' if accepts(word) else 'reject'}")
