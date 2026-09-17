r"""Test 1628 - ROUTE #178 control (gen #29): a helper that declares its own `#@ no_exception KeyError` (and reads a present key) is still callable under the caller's `#@ no_exception KeyError`.
"""
from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 1
def get() -> int:
    d: Dict[str, int] = {"a": 1}
    return d["a"]


#@ no_exception KeyError
#@ ensures \result == 1
def probe() -> int:
    return get()
