r"""Test 3260 — route #284 (expected FAIL): `f"{x:d}"` under `no_exception \all` PROVED (the #281 guard was computed but
never emitted for a literal spec: the test read the operand's WhyML type instead of the presentation type). CPython 3.11+ raises `ValueError` (Exceeds the limit (4300 digits) for integer string conversion) for
`x = 10**5000`; the rendering now owes `|x| < 10**4300` under `no_exception`, which nothing establishes.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    s = f"{x:d}"
    return 1


if __name__ == "__main__":
    try:
        f(10**5000)
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
