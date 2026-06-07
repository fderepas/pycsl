"""Test 0625 — negative: a collection binder ranges over ALL collections (07-1311 Q4 non-vacuity).

`\\forall a : list; \\length(a) >= 1` is FALSE — the empty list has length 0 — so it must be
refuted, confirming the `list` binder genuinely ranges over every array (including empty).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


#@ ensures \forall a : list; \length(a) >= 1
#@ assigns \nothing
def f() -> int:
    return 0
