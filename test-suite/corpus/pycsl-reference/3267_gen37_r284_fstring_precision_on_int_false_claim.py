r"""Test 3267 — route #284 (expected FAIL): `f"{x:.2}"` on an int under `no_exception \all` PROVED for a BOUNDED x.
CPython raises `ValueError` (Precision not allowed in integer format specifier) for every int.
"""
# pycsl-expected: FAIL


#@ requires 0 <= x and x <= 1000
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    s = f"{x:.2}"
    return 1


if __name__ == "__main__":
    try:
        f(5)
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
