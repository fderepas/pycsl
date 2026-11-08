r"""Test 4861 -- gen #37 route #361 (expected FAIL): witness r26: `_: KW_ONLY` sentinel read as `d._` under `no_exception \all` PROVED (CPython AttributeError). REFUSED (PYCSL-R361-DATACLASS-PSEUDO-FIELD, route #361).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, KW_ONLY

@dataclass
class D:
    x: int
    _: KW_ONLY
    y: int = 0

#@ no_exception \all
def f(d: D) -> int:
    return d._

if __name__ == "__main__":
    print(f(D(1)))
