r"""Test 6569 -- route #436 (expected FAIL): red team 34 witness `t9_split_loop` (getting-better/open-routes/witnesses-r436/t9_split_loop.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str, n: int) -> int:
    k = 0
    for w in s.split(",", n):
        k += 1
    return k


if __name__ == "__main__":
    try:
        r = f("a,b", 10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
