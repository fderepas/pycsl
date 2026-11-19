r"""Test 1915 — gen #33 (expected PASS): ROUTE #228's NEGATIVE CONTROL.

Identical to 1914 except that the second struct format is `'<hL'`, whose fold
(1127449053) differs from `'<bb6x'`'s (1322019588). The route #228 guard must NOT fire
here: it refuses a COLLISION, not a struct program.

THIS FILE IS THE HALF THAT MAKES 1914 MEAN ANYTHING. A guard that raised on every fold
would refuse 1914 too, and the plane would report a clean green over a verifier that had
stopped accepting `struct.pack` at all. `bin/check-stable-hash-fold-injectivity.py` runs
both directions for the same reason.

WHY THE POSTCONDITION IS A DISJUNCTION, which is the strongest PROVABLE claim here and
is worth stating rather than hiding behind `ensures True`. CPython returns 0 (8 != 6), but
the model cannot prove that: `struct_pack_i2` applied to two DIFFERENT folded constants
gives two unrelated terms, so nothing relates `Array.length a` to `Array.length b` and
NEITHER branch is decided. `\result == 0` is therefore true of the program and unprovable
of the model. `\result == 0 || \result == 1` is provable — both branches return one of
them — and it is a real claim about the function rather than a tautology, which is what
`bin/check-claim-vacuity.py` exists to insist on. This file's job is ACCEPTANCE: that PyCSL
still emits and type-checks a struct program whose formats do not collide.
"""
import struct  # noqa


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def go() -> int:
    a = struct.pack('<bb6x', 1, 2)
    b = struct.pack('<hL', 1, 2)
    if len(a) == len(b):
        return 1
    return 0
