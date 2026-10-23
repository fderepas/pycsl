r"""Test 1382 — ROUTE #136: a DYNAMIC (non-constant) `exec` at module scope rebinds the folded constant `N`; `exec_splice` splices only a CONSTANT exec and defers the rest to "scope havoc + frame taint", which only withholds `\in_scope`'s decided-false direction and (in the typed model) taints the heap — neither touches a folded VALUE. `f()` PROVED `\result == 3` while CPython returns 5. A dynamic `exec` that can bind into the module namespace is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3
exec("N" + " = 5")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
