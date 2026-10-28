r"""Test 6568 -- route #436 (expected FAIL): red team 34 witness `t7_split_ens` (getting-better/open-routes/witnesses-r436/t7_split_ens.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str, n: int) -> int:
    return len(s.split(" ", n))


if __name__ == "__main__":
    try:
        r = f("a b", 2**63)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
