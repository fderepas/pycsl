r"""Test 3115 — route #281 (expected FAIL): `s = f"v={x}"` under `no_exception \all` PROVED. CPython 3.11+ raises `ValueError` (Exceeds the
limit (4300 digits) for integer string conversion) for `x = 10**5000`; the conversion now owes
`|x| < 10**4300` under `no_exception`, which nothing establishes.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    s = f"v={x}"
    return 1


if __name__ == "__main__":
    try:
        f(10**5000)
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
