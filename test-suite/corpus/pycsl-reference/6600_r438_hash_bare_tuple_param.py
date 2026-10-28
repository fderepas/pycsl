r"""Test 6600 -- route #438 (expected FAIL): red team 34 w00: `hash(t)` of a parameter `t: tuple` under `no_exception \all`; `f(([1],))`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(t: tuple) -> int:
    return hash(t)


if __name__ == "__main__":
    try:
        r = f(([1],))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
