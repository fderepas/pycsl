"""Test 0822 — WL-05 regression guard (POSITIVE): LOCAL dict write-read-back still proves.

wrong-lowering-to-fix.md §WL-05. The complement of the 0820 rejection: a mutation of
a LOCAL dict (which IS a `ref`, so it has a genuine mutation frame) is faithfully
modelled and PROVES. After `d["a"] = 5`, reading `d["a"]` yields `5`. This guards the
WL-05 fix from over-rejecting: only dict/set PARAMETER mutation is out of scope; LOCAL
collection mutation is fully supported. If this ever FAILS, the fix has over-reached
and broken the faithful local-dict model.
"""
_ = 0  # anchor
from typing import Dict


#@ ensures \result == 5
def local_dict_write_readback() -> int:
    d: Dict[str, int] = {}
    d["a"] = 5
    return d["a"]
