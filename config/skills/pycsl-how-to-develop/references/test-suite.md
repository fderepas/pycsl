# Test Suite Structure

Load when adding reference tests, debugging the traceability matrix,
or working with the dual-oracle runner.

## Reference Tests (`test-suite/corpus/pycsl-reference/`)

Numbered test files (`0001.py` – `0190.py`+) exercising specific annotation features. Each test has:

```python
"""Test 0006 — PyCSL Annotation Reference 2.3.1"""
""  # pycsl
#@ class invariant self._value >= 0
class Counter:
    ...
if __name__ == "__main__":
    c = Counter()
    assert c.increment(5) == 5
```

## Annotations Reference (`test-suite/annotations.md`)

The authoritative document listing all PyCSL annotations. Numbered sections and table rows. **NEVER change existing numbering** — only append or insert within sections.

## Traceability (`test-suite/traceability-pycsl.md`)

Maps each annotation reference item (e.g., `2.3.1`) to test IDs:

```text
| 2.3.1 | Class invariant | 0006, 0076, 0077 | PASS |
```

## Dual-Oracle Runner (`test-suite/run_suite.py`)

Runs tests through:
1. **Static oracle** — compiles to WhyML and runs Why3/Alt-Ergo
2. **Dynamic oracle** — instruments contracts as Python assertions and runs
