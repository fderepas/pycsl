r"""Test 7284 -- route #472 (red team 38, expected FAIL: PROVED at base without --import-path, REFUSED): `import pycsl` -- `pycsl` is the VERIFIER's own script, not a module on the program's path; CPython ModuleNotFoundError.
"""
# pycsl-expected: FAIL
import pycsl


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
