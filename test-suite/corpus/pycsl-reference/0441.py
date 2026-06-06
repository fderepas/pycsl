"""0441 — cross-module class resolution (Layer A).

Imports `Counter` from `multi_file_lib.base_counter`, constructs it, and reads
its default field. This requires the imported class's record (fields, defaults,
class invariant) to cross the module boundary into the importer's IR. Without
Layer A, `Counter` is absent from the importer's record table — `Counter()`
lowers to an opaque call and `d.start` to an opaque getattr — so `ensures
\\result == 7` cannot be discharged. With Layer A, `Counter()` is record
construction (defaults from the imported `__init__`) and `d.start` reads `7`.
"""
from multi_file_lib.base_counter import Counter


#@ ensures \result == 7
def make_and_read() -> int:
    d = Counter()
    return d.start


if __name__ == "__main__":
    assert make_and_read() == 7
    print("PASS")
