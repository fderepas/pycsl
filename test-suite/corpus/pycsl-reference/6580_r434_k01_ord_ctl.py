r"""Test 6580 -- route #434 (expected PASS): CONTROL: `ord(s)` with `requires len(s) == 1`, `ord(t[1])` with `len(t) >= 2`, `ord("a")` under `no_exception \all` (CPython ok). PROVED at candidate.
"""
# pycsl-expected: PASS
#@ requires len(s) == 1 and len(t) >= 2
#@ no_exception \all
def f(s: str, t: str) -> int:
    a = ord(s)
    b = ord(t[1])
    c = ord("a")
    return a + b + c


if __name__ == "__main__":
    print("result", f("x", "yz"))
