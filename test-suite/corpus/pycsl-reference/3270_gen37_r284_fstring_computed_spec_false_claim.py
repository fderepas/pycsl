r"""Test 3270 — route #284 (expected FAIL): `f"{x:{w}}"` (a COMPUTED spec) under `no_exception \all` PROVED for a
BOUNDED x. With `w = "s"` CPython raises `ValueError`; a computed spec's validity is not modelled, so it
now owes `false` under a `no_exception` covering `ValueError`.
"""
# pycsl-expected: FAIL


#@ requires 0 <= x and x <= 1000
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int, w: str) -> int:
    s = f"{x:{w}}"
    return 1


if __name__ == "__main__":
    try:
        f(5, "s")
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
