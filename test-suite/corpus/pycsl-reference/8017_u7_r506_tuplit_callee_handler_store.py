r"""Test 8017 -- route #506 (expected FAIL, --memory-model store: a Why3 frame error of the mode at base (`store` does not occur), now REFUSED by name PYCSL-R506-TRIGGER-SITE-UNLOWERED): un-claimed g evaluates `t = (1, 10 // n)`; f's `except ZeroDivisionError: return 0` under `ensures \result == n + 1` was dead in the model; CPython f(0) returns 0)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
#@ ensures \result == n + 1
def g(n: int) -> int:
    t = (1, 10 // n)
    return n + 1


#@ ensures \result == n + 1
def f(n: int) -> int:
    try:
        return g(n)
    except ZeroDivisionError:
        return 0


if __name__ == "__main__":
    try:
        r = f(0)
        print("VIOLATION contract" if r != 1 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
