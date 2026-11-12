"""Reproducible compilation/execution timings; run with python3 -m examples.benchmark."""
import json
import platform
import statistics
import time

from klean.compiler import compile_source
from klean.vm import execute


def main():
    cases = {
        "3000_statements": "print(1);" * 3000,
        "100_term_expression": "print(" + "+".join(["1"] * 100) + ");",
        "10000_loop_iterations": "let n: int = 0; while (n < 10000) { n + 1 -> n; } print(n);",
    }
    report = {"python": platform.python_version(), "platform": platform.platform(),
              "repetitions": 5, "timings_ms": {}}
    for name, source in cases.items():
        compile_times, run_times = [], []
        for _ in range(5):
            start = time.perf_counter()
            result = compile_source(source)
            if result.diagnostics:
                raise RuntimeError(result.diagnostics)
            compiled = time.perf_counter()
            execute(result.bytecode, lambda _: None)
            finished = time.perf_counter()
            compile_times.append((compiled - start) * 1000)
            run_times.append((finished - compiled) * 1000)
        report["timings_ms"][name] = {
            "compile_median": round(statistics.median(compile_times), 3),
            "execute_median": round(statistics.median(run_times), 3),
        }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
