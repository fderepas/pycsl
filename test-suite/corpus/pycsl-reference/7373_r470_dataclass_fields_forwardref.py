r"""Test 7373 -- route #470 (expected FAIL): executor x2 bypass probe -- a dataclass field annotated with an undefined name, then `X = 1 // isinstance(C.__dataclass_fields__['x'].type, str)` at module level: #461 keeps the annotation that did not evaluate as its SOURCE STRING, CPython 3.14 records a ForwardRef (ZeroDivisionError at import). PROVED at base daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R461-IMPORT-RAISES, `__dataclass_fields__` of a synthesized class).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class C:
    x: UndefZZ = 0


X = 1 // isinstance(C.__dataclass_fields__['x'].type, str)


#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    print(f(1))
