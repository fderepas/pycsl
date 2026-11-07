r"""Test 7282 -- route #472 (red team 38, expected FAIL: PROVED at base without --import-path, REFUSED): `import frontend` -- `frontend` is a package of the VERIFIER, not a module on the program's path; CPython ModuleNotFoundError.
"""
# pycsl-expected: FAIL
import frontend


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
