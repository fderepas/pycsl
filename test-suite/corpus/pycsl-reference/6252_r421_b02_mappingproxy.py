r"""Test 6252 -- route #421 (expected FAIL): red team 33 witness `b02_mappingproxy` (getting-better/open-routes/witnesses-r421/b02_mappingproxy.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
import types
K = types.MappingProxyType({})


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
