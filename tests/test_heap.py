"""Managed allocation, tracing roots, reclamation, and heap-pressure failures."""
import unittest

from klean.compiler import compile_source
from klean.heap import HeapError, ManagedHeap
from klean.vm import KleanRuntimeError, VirtualMachine


class HeapTests(unittest.TestCase):
    def machine(self, source, limit=100):
        compiled = compile_source(source)
        self.assertEqual(compiled.diagnostics, [])
        output = []
        vm = VirtualMachine(compiled.bytecode, output.append, max_heap_slots=limit)
        vm.run()
        return vm, output

    def test_dynamic_and_empty_arrays(self):
        _, output = self.machine('''
            let n: int = 3; let a: int[] = array(n, 4); 9 -> a[1];
            print(a); print(len(a)); print(array(0, false)); print(len(array(0, 1)));
        ''')
        self.assertEqual(output, ['[4, 9, 4]', '3', '[]', '0'])

    def test_explicit_collection_reclaims_dead_scope_objects(self):
        vm, output = self.machine('''
            if (true) { let temporary: int[] = array(4, 7); print(len(temporary)); }
            print(collect() > 0);
        ''')
        self.assertEqual(output, ['4', 'true'])
        self.assertEqual(vm.heap.stats().live_objects, 0)
        self.assertEqual(vm.heap.stats().used_slots, 0)

    def test_automatic_collection_under_small_budget(self):
        vm, output = self.machine('''
            let i: int = 0;
            while (i < 50) { let a: int[] = array(4, i); i + a[0] * 0 + 1 -> i; }
            print(i);
        ''', limit=10)
        self.assertEqual(output, ['50'])
        self.assertGreater(vm.heap.stats().collections, 0)
        self.assertGreater(vm.heap.stats().reclaimed_objects, 0)
        self.assertLessEqual(vm.heap.stats().peak_slots, 10)

    def test_globals_stack_and_call_frames_are_roots(self):
        vm, output = self.machine('''
            let global: int[] = [7];
            fn keep(a: int[], ignored: int) -> int {
                let local: int[] = [8]; let freed: int = collect();
                return a[0] + local[0] + global[0];
            }
            print(keep([9], collect())); print(global);
        ''', limit=12)
        self.assertEqual(output, ['24', '[7]'])
        vm.heap.collect()
        self.assertEqual(vm.heap.stats().live_objects, 1)

    def test_returned_array_survives_collection(self):
        _, output = self.machine('''
            fn make() -> int[] { let a: int[] = array(2, 6); return a; }
            let saved: int[] = make(); let freed: int = collect(); print(saved);
        ''', limit=9)
        self.assertEqual(output, ['[6, 6]'])

    def test_live_objects_prevent_allocation(self):
        with self.assertRaisesRegex(KleanRuntimeError, 'Heap slot limit'):
            self.machine('let a: int[] = array(8, 0); let b: int[] = array(8, 1);', limit=10)

    def test_negative_huge_length_and_invalid_limit(self):
        for expression, fragment in [('array(-1, 0)', 'negative'),
                                     ('array(2147483647, 0)', 'Heap slot limit')]:
            with self.subTest(expression=expression):
                with self.assertRaisesRegex(KleanRuntimeError, fragment):
                    self.machine(f'print({expression});')
        with self.assertRaisesRegex(ValueError, 'positive'):
            ManagedHeap(lambda: [], max_slots=0)

    def test_array_builtin_type_and_arity_errors(self):
        for source in ['print(array(true, 0));', 'print(array(2, [1]));',
                       'print(array(2));', 'print(len(1));', 'print(len());',
                       'print(collect(1));']:
            with self.subTest(source=source):
                result = compile_source(source)
                self.assertTrue(result.diagnostics)
                self.assertIsNone(result.bytecode)

    def test_unit_tracing_handles_cycles_and_stale_references(self):
        roots = []
        heap = ManagedHeap(lambda: roots, max_slots=10)
        first = heap.allocate([0])
        second = heap.allocate([first])
        heap.get(first)[0] = second
        roots.append(first)
        self.assertEqual(heap.collect(), 0)
        roots.clear()
        self.assertEqual(heap.collect(), 2)
        with self.assertRaisesRegex(HeapError, 'reclaimed'):
            heap.get(first)

    def test_zero_length_arrays_still_consume_headers(self):
        roots = []
        heap = ManagedHeap(lambda: roots, max_slots=1)
        roots.append(heap.allocate([]))
        self.assertEqual(heap.stats().used_slots, 1)
        with self.assertRaisesRegex(HeapError, 'Heap slot limit'):
            heap.allocate([])

    def test_transient_allocation_values_are_roots(self):
        heap = ManagedHeap(lambda: [], max_slots=4)
        child = heap.allocate([3])
        garbage = heap.allocate([])
        parent = heap.allocate([child])
        self.assertEqual(heap.get(parent), [child])
        self.assertEqual(heap.get(child), [3])
        with self.assertRaises(HeapError):
            heap.get(garbage)
