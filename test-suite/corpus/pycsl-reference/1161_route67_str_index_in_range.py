"""1161 — ROUTE #67 POSITIVE CONTROL: a VALID string index still discharges.

The bound is exact (`in_bounds (String.length s) i`), so this is a real obligation and not a
ban on string indexing. Without it, refusing every `s[i]` would satisfy 1160.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    s = "ab"
    return ord(s[1])
