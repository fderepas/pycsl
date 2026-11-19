r"""Test 6281 -- route #421 (expected FAIL): red team 33 witness `h19_glob_dict_get` (getting-better/open-routes/witnesses-r421/h19_glob_dict_get.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
def mk() -> list:
    return [1]


K = mk()


#@ no_exception \all
def f() -> int:
    d = {1: 2}
    return d.get(K, 0)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
