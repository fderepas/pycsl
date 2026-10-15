r"""Test 2215 — route #239 (expected PASS): value-faithful control for 2208. A `None`-ambiguous
local read after an int rebinding reads THAT binding (`!x` = 6): `\result == 6` PROVES now,
where the per-name opaque `pycsl_erased_x` could not (FAIL at f926a808). CPython: 6.
"""
# pycsl-expected: PASS


#@ ensures \result == 6
#@ assigns \nothing
def f(c: int) -> int:
    x = None
    if c > 0:
        x = 5
    x = 6
    return x
