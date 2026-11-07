r"""Test 1840 — gen #31 (expected FAIL/REFUSED): `bounded_int(8)` names a Why3 module that
does not exist.

`#@ assumes bounded_int(N)` lowers to `use mach.int.Int<N>` with N interpolated straight
from the directive, and Why3's `mach/int.mlw` defines EXACTLY Int16, Int31, Int32, Int63 and
Int64 — there is no Int8. So this file used to end on

    Module Int8 not found in library mach.int
    [-] Verification FAILED or INCOMPLETE.

a WHY3 LIBRARY error for a directive PyCSL had accepted, with nothing to tell the reader
which widths exist. It FAILS CLOSED, so this is a diagnosability defect rather than a
soundness one — the same family as the six broken advice messages gen #30's audit repaired:
the compiler told the user to write something that does not compile, and said nothing when
they did.

annotations.md documented the form as `bounded_int(N)` with N unconstrained ("Use
`mach.int.IntN` types"). The width set is Why3's, not PyCSL's, and the table now says so.

FOUND BY `bin/check-directive-enforcement.py`, on the SATISFYING half of the `assumes` pair
— which is exactly what that half is for. A violating program that fails tells you nothing
if the honest program fails too.

CONTROL: 1841 (`bounded_int(32)`, a supported width, still verifies and still generates the
overflow VC).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ assumes bounded_int(8)
#@ requires 0 <= x and x <= 100
#@ ensures \result >= 0
def f(x: int) -> int:
    return x + 20
