r"""Test 6280 -- route #421 (expected FAIL): red team 33 witness `h16_glob_tuple_component` (getting-better/open-routes/witnesses-r421/h16_glob_tuple_component.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
def mk() -> list:
    return [1]


K = mk()


#@ no_exception \all
def f() -> int:
    s = {(1, K)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
