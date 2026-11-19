r"""Test 6653 -- route #440 A1 (expected FAIL): a file `Codec.to_bytes` admitted `n.to_bytes(1, "big")` on an `int` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `x002_realistic_to_bytes.py`); CPython raises OverflowError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

class Codec:
    def to_bytes(self, n: int, width: int) -> int:
        return 0


#@ no_exception \all
def encode_byte(n: int) -> int:
    return len(n.to_bytes(1, "big"))


if __name__ == "__main__":
    try:
        r = encode_byte(256)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
