r"""Test 2701 — route #259 (expected FAIL): `pow(x, 2, m)` raises `ValueError` for `m == 0`,
but route #160's `pow` check inspected only the EXPONENT, so `#@ no_exception \all` PROVED
with an unconstrained modulus at b35d9c5e. Now REFUSED unless the modulus is a nonzero literal.
"""
# pycsl-expected: FAIL


#@ no_exception \all
#@ assigns \nothing
def f(x: int, m: int) -> int:
    return pow(x, 2, m)


if __name__ == "__main__":
    try:
        f(2, 0)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
