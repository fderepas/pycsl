r"""Test 8016 -- route #506 (expected FAIL, --memory-model typed: a Why3 type error of the mode at base (`option` unbound in the set preamble), now REFUSED by name PYCSL-R506-TRIGGER-SITE-UNLOWERED): g claims `#@ no_exception ZeroDivisionError` and evaluates a set display `{10 // n}`; CPython g(0) raises ZeroDivisionError)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
#@ no_exception ZeroDivisionError
#@ ensures \result == n + 1
def g(n: int) -> int:
    s = {10 // n}
    return n + 1


if __name__ == "__main__":
    try:
        r = g(0)
        print("VIOLATION contract" if r != 1 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
