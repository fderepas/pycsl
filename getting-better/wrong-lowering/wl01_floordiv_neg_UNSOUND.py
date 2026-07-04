"""WL-01 UNSOUND — Python floor-division `//` on a negative divisor is lowered to
Why3 int.EuclideanDivision.div, which diverges from Python's floored semantics.

CPython ground truth:   (-7) // (-2) == 3      (floor of 3.5)
Why3 EuclideanDivision: div (-7) (-2) == 4      (nonneg remainder convention)

DETECTOR D3 (false twin). VERDICT: this driver's `ensures \result == 4` is FALSE
of Python (real value 3) yet PyCSL PROVES it -> UNSOUND. The TRUE claim
(`== 3`, see wl01_floordiv_neg_TRUE) canNOT be proven. No `requires` guards the
negative divisor, so the wrong value ships as a green proof.
Cross-ref: translational-reference G1 (documents a divergence but with a WRONG
example -7//2, which actually AGREES; the real divergence is a negative DIVISOR).
"""
_ = 0
#@ ensures \result == 4
def f() -> int:
    return (-7) // (-2)

if __name__ == "__main__":
    assert f() == 3   # CPython
