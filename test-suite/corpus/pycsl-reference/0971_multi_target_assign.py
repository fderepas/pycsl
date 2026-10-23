"""Test 0971 — `a = b = v` binds EVERY target, and dropping the tail PROVED A FALSE
POSTCONDITION.

`Module5_IREmitter._py_stmt_assign` opens with `target = stmt.targets[0]` and never looks
at the rest, so in `a = b = 5` the binding of `b` did not exist in the model. When no other
statement assigns `b` the file at least failed L3-tc with `unbound function or predicate
symbol 'b'`; when another statement DID assign it, the initialisation was silently lost and
the local kept its DECLARATION DEFAULT.

MEASURED, before `frontend/desugar.normalize_stores`: this exact `banded` body with the
postcondition `n <= 0 ==> \\result == 0` reported `Verification SUCCESS` — while `banded(0)`
returns 5 in Python. A false statement about the program, proved. The model had `b`
declared `ref 0` and assigned only inside the `if`.

`normalize_stores` expands the statement into one assignment per target. The RHS is
re-mentioned only when it is a `Constant` or a `Name` — both SHARE their object, so the
aliasing Python guarantees (`a = b = []` binds ONE list to both names) is preserved; every
other RHS is bound to a fresh temporary first, so it is evaluated exactly once, as Python
does. `paired` witnesses the temporary route: its RHS is a CALL, which may not be
re-mentioned.

NEGATIVE TEST: with the normalization removed, `banded`'s `n <= 0 ==> \\result == 5` goal
goes Unknown (the model returns 0) and `paired` fails L3-tc on an unbound `q`.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires True
#@ ensures n > 0 ==> \result == 7
#@ ensures n <= 0 ==> \result == 5
#@ assigns \nothing
def banded(n: int) -> int:
    a = b = 5
    if n > 0:
        b = 7
    return a * 0 + b


#@ requires True
#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3


#@ requires True
#@ ensures \result == 6
#@ assigns \nothing
def paired() -> int:
    p = q = three()
    return p + q
