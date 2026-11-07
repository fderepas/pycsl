r"""Test 6509 -- route #432 (expected FAIL): `x: str = None; x.strip()` (g4 probe) under `#@ no_exception \all`. Not PROVED at base 1c083dcbe either (refused by the default-annotation rule, a `None` default for `x: str`); a RULE witness: #432 now refuses it first (a parameter defaulted to `None` holds `None`). CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: str = None) -> int:
    return len(x.strip())


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
