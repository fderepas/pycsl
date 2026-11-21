r"""Test 6587 -- route #434 (expected PASS): CONTROL (the advice of `PYCSL-R434-ORD-PATH` followed for witness 6579): `ord(str(p)[0])` with `p: Path`, `requires len(str(p)) >= 1`, under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from pathlib import Path


#@ requires len(str(p)) >= 1
#@ no_exception \all
def f(p: Path) -> int:
    return ord(str(p)[0])


if __name__ == "__main__":
    print("result", f(Path("a")))
