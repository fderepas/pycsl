r"""Test 6588 -- route #435 (expected FAIL): `str.upper(p)` with `p: Path` under `no_exception \all`, f(Path("a")) (CPython TypeError: descriptor 'upper' for 'str' objects doesn't apply to a 'PosixPath' object): the front end erases the `Path` annotation to `str`, so #435's `str` row admitted it at 86f9efa51; REFUSED (`PYCSL-R434-ORD-PATH`). PROVED at base 78b519f63 and at 86f9efa51.
"""
# pycsl-expected: FAIL
from pathlib import Path


#@ no_exception \all
def f(p: Path) -> int:
    s = str.upper(p)
    return 0


if __name__ == "__main__":
    try:
        print("result", f(Path("a")))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
