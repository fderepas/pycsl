r"""Test 6573 -- route #434 (expected FAIL): an alias `q = p.parent; ord(q)` of a Path (CPython TypeError): REFUSED (`PYCSL-R434-ORD-PATH`, the alias is followed). PROVED at base 78b519f63 and at 86f9efa51.
"""
# pycsl-expected: FAIL
from pathlib import Path


#@ requires len(str(p.parent)) == 1
#@ no_exception \all
def f(p: Path) -> int:
    q = p.parent
    return ord(q)


if __name__ == "__main__":
    try:
        print("result", f(Path("a/b")))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
