"""1168 — ROUTE #69 POSITIVE CONTROL: ASCII `ord` is untouched, and `len` was always right.

For an ASCII literal the byte model and Python agree, so `ord("a") < 256` is TRUE and must
keep proving. (The exact value `== 97` is NOT derivable — Why3 does not compute `Char.code`
of a literal — so the control claims the BOUND, which is precisely what route #69 showed to
be false for a non-ASCII literal and true for an ASCII one.) `len` of a NON-ASCII literal is also correct already (it folds from the Python
literal, giving 1) — which is what makes the route an INTERNAL INCONSISTENCY rather than a
uniformly byte-based model, and why the repair refuses `ord` rather than the literal.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result < 256
#@ assigns \nothing
def f() -> int:
    return ord("a")
