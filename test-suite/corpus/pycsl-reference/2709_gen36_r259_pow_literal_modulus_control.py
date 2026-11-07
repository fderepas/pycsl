r"""Test 2709 — route #259 CONTROL (expected PASS): `pow(x, 2, 7)` — a non-negative literal
exponent and a NONZERO literal modulus cannot raise, so `#@ no_exception \all` still
proves (the route #160 convention).
"""


#@ no_exception \all
#@ assigns \nothing
def f(x: int) -> int:
    return pow(x, 2, 7)


if __name__ == "__main__":
    assert f(3) == 2
