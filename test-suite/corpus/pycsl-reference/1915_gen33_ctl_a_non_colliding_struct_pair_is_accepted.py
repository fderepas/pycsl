r"""Test 1915 — gen #33 (expected PASS): ROUTE #228's NEGATIVE CONTROL.

Identical to 1914 except that the second struct format is `'<hL'`, whose fold
(1127449053) differs from `'<bb6x'`'s (1322019588). The route #228 guard must NOT fire
here: it refuses a COLLISION, not a struct program.

THIS FILE IS THE HALF THAT MAKES 1914 MEAN ANYTHING. A guard that raised on every fold
would refuse 1914 too, and the plane would report a clean green over a verifier that had
stopped accepting `struct.pack` at all. `bin/check-stable-hash-fold-injectivity.py` runs
both directions for the same reason.

The postcondition here is the TRUE one: 8 != 6, so `go()` returns 0 in CPython, and
nothing about the two distinct `struct_pack_i2` applications relates their lengths — so
`\result == 0` is NOT provable either, and the honest contract is `ensures True`. What is
asserted is only that the file is ACCEPTED (emits and type-checks).
"""
import struct  # noqa


#@ requires True
#@ ensures True
#@ assigns \nothing
def go() -> int:
    a = struct.pack('<bb6x', 1, 2)
    b = struct.pack('<hL', 1, 2)
    if len(a) == len(b):
        return 1
    return 0
