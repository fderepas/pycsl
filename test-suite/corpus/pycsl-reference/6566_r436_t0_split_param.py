r"""Test 6566 -- route #436 (expected FAIL): red team 34 witness `t0_split_param` (getting-better/open-routes/witnesses-r436/t0_split_param.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str, n: int) -> int:
    return len(s.split(" ", n))


if __name__ == "__main__":
    try:
        r = f("a b", 10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
