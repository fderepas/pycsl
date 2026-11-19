r"""Test 6450 -- route #431 (expected FAIL): rg-dict-r3 probe l3o (getting-better/systematic-soundness-r3/rg-dict-r3/probes/l3o_finally_return_none_hash.py). A `return` in `finally:` swallows the ambient hash TypeError of an un-claimed function, so `ensures out[0] == 1` PROVED at base 725a1c7e5; CPython leaves out[0] == 2 (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R431-FINALLY-JUMP-SWALLOWS-EXCEPTION).
"""
# pycsl-expected: FAIL
from typing import Dict, Any, List


#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(m: Dict[str, Any], out: List[int]) -> None:
    out[0] = 2
    try:
        n = hash(m.get("a"))
        out[0] = 1
    finally:
        return


if __name__ == "__main__":
    o = [0]
    f({"a": [1]}, o)
    print("VIOLATION" if o[0] != 1 else "ok", o)
