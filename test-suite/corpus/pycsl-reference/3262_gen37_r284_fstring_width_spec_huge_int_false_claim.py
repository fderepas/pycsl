r"""Test 3262 — route #284 (expected FAIL): `f"{x:5}"` (width only, no presentation type = decimal) under `no_exception \all` PROVED. CPython 3.11+ raises `ValueError` (Exceeds the limit (4300 digits) for integer string conversion) for
`x = 10**5000`; the rendering now owes `|x| < 10**4300` under `no_exception`, which nothing establishes.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    s = f"{x:5}"
    return 1


if __name__ == "__main__":
    try:
        f(10**5000)
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
