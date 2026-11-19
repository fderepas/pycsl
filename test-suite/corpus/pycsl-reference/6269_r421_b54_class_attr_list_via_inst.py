r"""Test 6269 -- route #421 (expected FAIL): red team 33 witness `b54_class_attr_list_via_inst` (getting-better/open-routes/witnesses-r421/b54_class_attr_list_via_inst.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class C:
    L = [1]


K = C().L


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
