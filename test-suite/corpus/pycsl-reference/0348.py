"""Test 0348 — Multi-argument `range(start, stop)` under full proof.

Exercises Module6's `range(start, stop)` lowering: the loop index
initialises at `start` and the bound becomes `stop`. The body sees
`!_idx_i` as the loop variable.

`0327`/`0328` cover the parse-level case under `--no-proof`; this
test targets full SMT discharge with loop invariants on a sum
accumulator.
"""
#@ requires start >= 0
#@ requires stop >= start
#@ ensures \result >= 0
#@ assigns \nothing
def sum_range(start: int, stop: int) -> int:
    total = 0
    #@ loop invariant total >= 0
    #@ loop invariant start <= i and i <= stop
    #@ loop variant stop - i
    for i in range(start, stop):
        if i >= 0:
            total += i
    return total

if __name__ == "__main__":
    assert sum_range(0, 0) == 0
    assert sum_range(0, 3) == 0 + 1 + 2
    assert sum_range(2, 5) == 2 + 3 + 4
    assert sum_range(10, 10) == 0
    print("PASS")
