r"""Test 6579 -- route #434 (expected FAIL): `ord(p)` with `p: Path` under `requires len(str(p)) == 1` and `no_exception \all`, f(Path("a")) (CPython TypeError: a Path is not a str): the front end erases the `Path` annotation to `str`, so only the length was owed; REFUSED (`PYCSL-R434-ORD-PATH`). PROVED at base 78b519f63 and at 86f9efa51 (increment 1).
"""
# pycsl-expected: FAIL
from pathlib import Path


#@ requires len(str(p)) == 1
#@ no_exception \all
def f(p: Path) -> int:
    return ord(p)


if __name__ == "__main__":
    try:
        print("result", f(Path("a")))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
