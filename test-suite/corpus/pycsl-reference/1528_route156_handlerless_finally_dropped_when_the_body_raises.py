r"""Test 1528 - ROUTE #156 (gen #29): `try: raise ValueError / finally: x = 7` nested inside `try ... except ValueError: pass`; the inner `finally` has no handlers and its body jumps out, so Module 6 dropped the block and `\result != 7` PROVED; CPython 7. Route #21 refused only a `finally` WITH handlers; this half is now refused too (PYCSL-R156).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result != 7
def probe() -> int:
    x = 0
    try:
        try:
            raise ValueError
        finally:
            x = 7
    except ValueError:
        pass
    return x

