r"""Test 4864 -- gen #37 route #361 (expected FAIL): (new) string annotation `"dataclasses.InitVar[int]"` read under `no_exception \all`. REFUSED (PYCSL-R361-DATACLASS-PSEUDO-FIELD, route #361).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
import dataclasses

@dataclass
class D:
    x: int
    k: "dataclasses.InitVar[int]"

#@ no_exception \all
def f(d: D) -> object:
    return d.k

if __name__ == "__main__":
    print(f(D(1, 2)))
