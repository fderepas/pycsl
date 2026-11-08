r"""Test 6586 -- route #434 (expected FAIL): `ord(p[0])` with `p: Path` (CPython TypeError: a Path is not subscriptable): REFUSED (`PYCSL-R434-ORD-PATH`). PROVED at base 78b519f63 and at 86f9efa51.
"""
# pycsl-expected: FAIL
from pathlib import Path


#@ requires len(str(p)) >= 1
#@ no_exception \all
def f(p: Path) -> int:
    return ord(p[0])


if __name__ == "__main__":
    try:
        print("result", f(Path("a")))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
