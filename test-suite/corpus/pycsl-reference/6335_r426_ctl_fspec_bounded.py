r"""Test 6335 -- route #426 (expected PASS): CONTROL: f-string specs over an int under `no_exception \all` whose obligations hold: `{n:x}` / `{n:b}` (no bound), `{n:f}` / `{n:.2e}` / `{n:%}` with |n| <= 10**6 (<= DBL_MAX), `{n:c}` with 0 <= n < 0x110000 (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires 0 <= n and n < 1000000
#@ no_exception \all
def f(n: int) -> int:
    a = f"{n:x}"
    b = f"{n:b}"
    c = f"{n:f}"
    d = f"{n:.2e}"
    e = f"{n:%}"
    g = f"{n:c}"
    return len(a) + len(b) + len(c) + len(d) + len(e) + len(g)


if __name__ == "__main__":
    print(f(65))
