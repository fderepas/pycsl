r"""Test 6572 -- route #434 (expected FAIL): an un-claimed callee `h(s): return ord(s)` called under `no_exception \all`, f("ab") (CPython TypeError): REFUSED (`PYCSL-R434-CALLEE-UNCHECKED-SITE`). PROVED at base 78b519f63.
"""
# pycsl-expected: FAIL
def h(s: str) -> int:
    return ord(s)


#@ no_exception \all
def f(s: str) -> int:
    return h(s)


if __name__ == "__main__":
    try:
        print("result", f("ab"))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
