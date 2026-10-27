r"""Test 6298 -- route #424 (expected FAIL): red team 33 witness `j23_cgi_glob` (getting-better/open-routes/witnesses-r424/j23_cgi_glob.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class K:
    def __class_getitem__(cls, item: int) -> list:
        return [item]


G = K[1]


#@ no_exception \all
def f() -> int:
    s = {G}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
