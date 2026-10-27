r"""Test 6283 -- route #422 (expected FAIL): red team 33 witness `c31_enum_value` (getting-better/open-routes/witnesses-r422/c31_enum_value.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
import enum


class E(enum.Enum):
    A = [1]


#@ no_exception \all
def f() -> int:
    k = E.A.value
    s = {k}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
