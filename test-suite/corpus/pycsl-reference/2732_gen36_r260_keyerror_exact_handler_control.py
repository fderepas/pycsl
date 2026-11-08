r"""Test 2732 — route #260 CONTROL (expected PASS): the exact-class handler `except KeyError`
around `raise KeyError` keeps working; CPython returns 7.
"""
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    r = 0
    try:
        raise KeyError("k")
    except KeyError:
        r = 7
    return r

if __name__ == "__main__":
    print(f())
