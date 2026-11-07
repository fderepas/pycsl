r"""Test 6564 -- route #435 (expected FAIL): red team 34 witness `c18_str_upper_list` (getting-better/open-routes/witnesses-r435/c18_str_upper_list.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: list) -> int:
    s = str.upper(x)
    return 0


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
