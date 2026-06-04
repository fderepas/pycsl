"""Test 0500 — collections: Counter increment via `c[k] += 1` (dict model).

Subscript augmented-assignment `c[k] += 1` now desugars to a store of `(c[k]) + 1` through the
proven map-update path — previously it was silently dropped (no Subscript arm in
`_py_stmt_augassign`). Two increments from the empty counter give `c[7] == 2`. (This desugaring
also fixes plain `arr[i] += v`.)"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import Counter


#@ ensures \result == 2
def count_twice() -> int:
    c = Counter()
    c[7] += 1
    c[7] += 1
    return c[7]
