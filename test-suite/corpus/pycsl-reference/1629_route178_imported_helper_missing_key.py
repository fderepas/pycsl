r"""Test 1629 - ROUTE #178 carrier (gen #29): an IMPORTED helper `get(d)` returning `d["b"]`, called under the caller's `#@ no_exception KeyError` on `d = {"a": 1}`, PROVED at HEAD (CPython KeyError). Imported stub bodies are in the IR and are now covered.
"""
# pycsl-expected: FAIL
from typing import Dict
_ = 0  # anchor
from multi_file_lib.r178_reader import get


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    v = get(d)
    return v * 0
