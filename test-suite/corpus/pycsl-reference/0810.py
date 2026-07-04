"""Test 0810 — target-dependent index with a CAPTURED offset `x[len(x)-c]`.

nested-list.md §8/§9 EXTENSION (target-dependent index, captured-param variant).
The comprehension `[x[len(x)-c] for x in a]` over `List[List[int]]` uses an index
that depends BOTH on the loop target `x` (via `len(x)`) AND a captured enclosing
param `c`. The index lifts to a pure int term `Seq.length (x) - c` over the
per-index row, and the captured `c` is threaded as an EXTRA parameter of the
abstract content-law val (`_lift_target_seq_index` collects it into the
free-var set). The law is
    forall i. result[i] = Seq.get (a[i]) (Seq.length (a[i]) - c)
— the SAME inner read the driver's own `\result[i] == a[i][len(a[i])-c]` lowers
to. Exercises the captured-free-var threading on the target-dependent path. No
new axiom (definitional `ensures`; Seq read/length laws are Why3 stdlib).
"""
_ = 0  # anchor
from typing import List

#@ requires c >= 1
#@ requires \forall i; 0 <= i and i < \length(a) ==> len(a[i]) >= c
#@ ensures \length(\result) == \length(a)
#@ ensures \forall i; 0 <= i and i < \length(a) ==> \result[i] == a[i][len(a[i]) - c]
#@ assigns \nothing
def drop_last_c(a: List[List[int]], c: int) -> List[int]:
    return [x[len(x) - c] for x in a]

if __name__ == "__main__":
    assert drop_last_c([[1, 2, 3], [4, 5]], 1) == [3, 5]
