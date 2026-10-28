r"""Test 6620 -- route #439 (expected FAIL): red team 34 j5: `import multi_file_lib.r439_hashlib as hl`; `hl.h(m)` where the UN-CLAIMED imported `h` hashes `m.get("a")` (`Dict[str, Any]`). PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R430-CALLEE-UNDERIVABLE-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict
import multi_file_lib.r439_hashlib as hl

#@ no_exception \all
#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    return hl.h(m)


if __name__ == "__main__":
    try:
        r = f({"a": [1]})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
