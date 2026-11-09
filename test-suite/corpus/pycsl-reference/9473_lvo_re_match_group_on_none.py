r"""Test 9473 -- lvO re.Match model (expected FAIL): a group read of an UNGUARDED match local is
`None.group(1)` when the subject does not match (CPython AttributeError), so the read carries the VC
`handle <> 0`, which must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_KV = re.compile(r"(\w+)=(\w+)")


#@ ensures True
#@ assigns \nothing
def key(s: str) -> str:
    m = _KV.match(s)
    return m.group(1)


if __name__ == "__main__":
    try:
        key("nomatch")
        print("result ok")
    except AttributeError:
        print("VIOLATION AttributeError")
