r"""Test 2507 — route #250 (expected PASS): CONTROLS under `--strict-float-finite`.

Dropping FLOAT-FINITE must not cost the claims that are TRUE in CPython for every float, NaN
included: a literal result (`\result == 1.5`), a body comparison guarded by the same comparison
in the precondition (`x >= 0.0` excludes NaN), order facts derived from a precondition, and
transitivity. The measured cost of the flag is elsewhere: `ensures \result == <float arithmetic>`
(0517, 1124) stops proving because the uninterpreted float op may yield NaN.
"""
# pycsl-flags: --strict-float-finite
# pycsl-expected: PASS


#@ ensures \result == 1.5
#@ assigns \nothing
def lit() -> float:
    return 1.5


#@ requires x >= 0.0
#@ ensures \result == 1
#@ assigns \nothing
def guarded(x: float) -> int:
    if x >= 0.0:
        return 1
    return 2


#@ requires x > 0.0
#@ ensures x >= 0.0 and x == x and not (x < 0.0)
#@ assigns \nothing
def derived(x: float) -> int:
    return 0


#@ requires x < y and y < z
#@ ensures x < z
#@ assigns \nothing
def transitive(x: float, y: float, z: float) -> int:
    return 0


if __name__ == "__main__":
    assert lit() == 1.5
    assert guarded(0.0) == 1
    assert derived(2.0) == 0
    assert transitive(1.0, 2.0, 3.0) == 0
