r"""Test 1548 - ROUTE #160 (gen #29, carrier of route #72): `"a".split("")` carries `receiver` with an UNDOTTED `func`, so #72's `(attr_call, split)` refusal never matched and `no_exception ValueError` PROVED; CPython raises.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    return len("a".split(""))

