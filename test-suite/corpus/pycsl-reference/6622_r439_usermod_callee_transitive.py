r"""Test 6622 -- route #439 (expected FAIL): NEW latent: the imported `mid(m)` (no set display of its own) calls `h(m)` of ANOTHER user module that hashes `m.get("a")`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R430-CALLEE-UNDERIVABLE-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict
from multi_file_lib.r439_hashmid import mid

#@ no_exception \all
#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    return mid(m)


if __name__ == "__main__":
    try:
        r = f({"a": [1]})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
