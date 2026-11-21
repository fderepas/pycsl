r"""Test 10076 -- lvU `shutil.which` (expected FAIL): the model types `shutil.which(..)` as the
`str | None` union of the RETURNING function, so a function declared `-> Optional[int]` that
returns it is REFUSED (PYCSL-R7U-EXT-WHICH-SHAPE), never lowered to an int answer. CPython returns a
`str`, so `\result` is not an int. Control: 10070.
"""
# pycsl-expected: FAIL
import shutil
from typing import Optional


#@ assigns \nothing
def where(cmd: str) -> Optional[int]:
    return shutil.which(cmd)


if __name__ == "__main__":
    r = where("sh")
    print("VIOLATION contract" if not (r is None or isinstance(r, int)) else "result", r)
