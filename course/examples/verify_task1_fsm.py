"""Check the transitions in the diagram against the Task 1 conditions."""

from itertools import product
from pathlib import Path
from xml.etree import ElementTree


root = ElementTree.parse(Path(__file__).with_name("task1_fsm.svg")).getroot()
states = {node.attrib["data-state"] for node in root.iter()
          if "data-state" in node.attrib}
initial = [node.attrib["data-state"] for node in root.iter()
           if node.get("data-initial") == "true"]
accepting = {node.attrib["data-state"] for node in root.iter()
             if node.get("data-accepting") == "true"}
assert len(initial) == 1
alphabet = "abcz"
transitions = {}
for edge in root.iter():
    if "data-from" not in edge.attrib:
        continue
    source, target = edge.get("data-from"), edge.get("data-to")
    assert source in states and target in states
    label = next(child for child in edge if child.tag.endswith("}text"))
    symbols = edge.get("data-symbols").split(",")
    assert "".join(label.itertext()).replace(" ", "").split(",") == symbols
    for symbol in symbols:
        assert (source, symbol) not in transitions, "Non-deterministic edge"
        transitions[source, symbol] = target
assert set(transitions) == set(product(states, alphabet)), "Incomplete DFA"


def accepts(word):
    state = initial[0]
    for symbol in word:
        state = transitions[state, symbol]
    return state in accepting


checked = 0
for length in range(9):
    for chars in product(alphabet, repeat=length):
        word = "".join(chars)
        expected = (word.startswith("a") and word.endswith("z")
                    and word.count("b") % 2 == 0)
        assert accepts(word) == expected, f"Incorrect result for {word!r}"
        checked += 1
print(f"PASS: complete DFA; checked all {checked:,} strings of lengths 0-8.")
for word in ["", "a", "az", "azz", "abbz", "abzbz", "abz", "azb", "baz"]:
    print(f"{word!r}: {'accept' if accepts(word) else 'reject'}")
