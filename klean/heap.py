"""VM-owned array heap with explicit tracing and mark-and-sweep collection.

Python stores the backing lists, but Klean object reachability, reclamation,
allocation accounting and limits are implemented here rather than delegated
to Python's garbage collector. A slot is one array header or one element.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


class HeapError(RuntimeError):
    pass


@dataclass(frozen=True)
class HeapRef:
    address: int


@dataclass(frozen=True)
class HeapStats:
    allocations: int
    collections: int
    reclaimed_objects: int
    live_objects: int
    used_slots: int
    peak_slots: int


class ManagedHeap:
    def __init__(self, roots: Callable[[], Iterable[object]], max_slots: int = 1_000_000):
        if max_slots <= 0:
            raise ValueError("Heap limit must be positive")
        self.roots = roots
        self.max_slots = max_slots
        self.objects: dict[int, list[object]] = {}
        self.next_address = 1
        self.used_slots = 0
        self.peak_slots = 0
        self.allocations = 0
        self.collections = 0
        self.reclaimed_objects = 0

    def get(self, reference: HeapRef) -> list[object]:
        try:
            return self.objects[reference.address]
        except KeyError:
            raise HeapError("Invalid or reclaimed heap reference") from None

    def _reserve(self, length: int, extra_roots: Iterable[object] = ()) -> None:
        if length < 0:
            raise HeapError("Array length must not be negative")
        slots = length + 1  # Even an empty array consumes a header slot.
        if slots > self.max_slots:
            raise HeapError("Heap slot limit exceeded")
        if self.used_slots + slots > self.max_slots:
            self.collect(extra_roots)
        if self.used_slots + slots > self.max_slots:
            raise HeapError("Heap slot limit exceeded: live arrays retain the available space")

    def _store(self, values: list[object]) -> HeapRef:
        reference = HeapRef(self.next_address)
        self.next_address += 1
        self.objects[reference.address] = values
        self.used_slots += len(values) + 1
        self.peak_slots = max(self.peak_slots, self.used_slots)
        self.allocations += 1
        return reference

    def allocate(self, values: list[object]) -> HeapRef:
        self._reserve(len(values), values)
        try:
            return self._store(values.copy())
        except MemoryError:
            raise HeapError("Host memory exhausted while allocating an array") from None

    def allocate_filled(self, length: int, fill: object) -> HeapRef:
        # Check the budget before constructing a potentially huge Python list.
        self._reserve(length, (fill,))
        try:
            return self._store([fill] * length)
        except MemoryError:
            raise HeapError("Host memory exhausted while allocating an array") from None

    def collect(self, extra_roots: Iterable[object] = ()) -> int:
        marked: set[int] = set()
        pending = [*self.roots(), *extra_roots]
        while pending:
            value = pending.pop()
            if isinstance(value, HeapRef) and value.address not in marked:
                values = self.get(value)
                marked.add(value.address)
                pending.extend(values)
        dead = [address for address in self.objects if address not in marked]
        for address in dead:
            self.used_slots -= len(self.objects.pop(address)) + 1
        self.collections += 1
        self.reclaimed_objects += len(dead)
        return len(dead)

    def stats(self) -> HeapStats:
        return HeapStats(self.allocations, self.collections, self.reclaimed_objects,
                         len(self.objects), self.used_slots, self.peak_slots)
