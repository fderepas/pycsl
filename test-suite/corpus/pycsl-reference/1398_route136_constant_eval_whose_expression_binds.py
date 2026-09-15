r"""Test 1398 — ROUTE #136: an `eval` binds through a walrus — and through any namespace builtin its expression reaches. `eval("globals().update({'N': 5})")` has no walrus and a compile-time-constant text, so the first cut of the repair let it through; `f()` PROVED `\result == 3` while CPython returns 5. A constant `eval` text naming `exec`/`eval`/`setattr`/`delattr`/`globals`/`vars`/`locals`/`getattr` is now treated as binding.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3
eval("globals().update({'N': 5})")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
