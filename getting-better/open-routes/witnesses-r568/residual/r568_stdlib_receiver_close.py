r"""r568 RESIDUAL (NOT covered by the #568 repair; PROVED at base 693e20184 and at HEAD under the default model):
an `Any` receiver of a STANDARD-LIBRARY class whose method changes an attribute (`io.StringIO.close()` sets
`closed`). No file method is named `close`, so the stub of `f.close()` stays frameless and the two state-keyed
`getattr(f, "closed", 0)` reads are one term. CPython: 2 (the claim is `\result == 1`).
"""
# pycsl-expected: FAIL
from typing import Any
import io

#@ requires True
#@ ensures \result == 1
#@ assigns f.closed
def caller(f: Any) -> int:
    x = getattr(f, "closed", 0)
    f.close()
    y = getattr(f, "closed", 0)
    if x or not y:
        return 1
    return 2

if __name__ == "__main__":
    print(caller(io.StringIO()))
