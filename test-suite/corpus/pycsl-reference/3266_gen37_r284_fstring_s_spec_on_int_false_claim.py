r"""Test 3266 — route #284 (expected FAIL): `f"{x:s}"` on an int under `no_exception \all` PROVED for a BOUNDED x.
CPython raises `ValueError` (Unknown format code 's' for object of type 'int') for every int: the spec
is invalid for the type, now decided at emit time and owed as `false`.
"""
# pycsl-expected: FAIL


#@ requires 0 <= x and x <= 1000
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    s = f"{x:s}"
    return 1


if __name__ == "__main__":
    try:
        f(5)
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
