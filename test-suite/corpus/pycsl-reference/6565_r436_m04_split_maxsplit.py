r"""Test 6565 -- route #436 (expected FAIL): red team 34 witness `m04_split_maxsplit` (getting-better/open-routes/witnesses-r436/m04_split_maxsplit.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(n: int) -> int:
    return len('a b'.split(' ', n))


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
