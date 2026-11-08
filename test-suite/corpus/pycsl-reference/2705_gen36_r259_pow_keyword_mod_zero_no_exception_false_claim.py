r"""Test 2705 — route #259 (expected FAIL): `pow(x, 2, mod=0)` raises `ValueError` exactly
like `pow(x, 2, 0)`, but the keyword was invisible to route #160's check (and dropped by
the lowering, `pow_2 x 2`), so `#@ no_exception \all` PROVED at b35d9c5e. Now `pow`'s
keywords are folded into their positions and the zero modulus is REFUSED.
"""
# pycsl-expected: FAIL


#@ no_exception \all
#@ assigns \nothing
def f(x: int) -> int:
    return pow(x, 2, mod=0)


if __name__ == "__main__":
    try:
        f(3)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
