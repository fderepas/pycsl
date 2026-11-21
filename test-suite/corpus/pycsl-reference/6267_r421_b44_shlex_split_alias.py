r"""Test 6267 -- route #421 (expected FAIL): red team 33 witness `b44_shlex_split_alias` (getting-better/open-routes/witnesses-r421/b44_shlex_split_alias.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
from shlex import split as sp
K = sp('a b')


#@ no_exception \all
def f() -> int:
    s = {K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
