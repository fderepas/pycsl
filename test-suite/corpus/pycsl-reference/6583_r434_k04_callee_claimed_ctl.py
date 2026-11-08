r"""Test 6583 -- route #434 (expected PASS): CONTROL: a callee claiming `no_exception \all` itself (`requires len(s) == 1`; `return ord(s)`) called under `no_exception \all` (CPython ok). PROVED at candidate.
"""
# pycsl-expected: PASS
#@ requires len(s) == 1
#@ no_exception \all
def h(s: str) -> int:
    return ord(s)


#@ requires len(s) == 1
#@ no_exception \all
def f(s: str) -> int:
    return h(s)


if __name__ == "__main__":
    print("result", f("a"))
