r"""Test 9901 -- lvS cap-re-gate-widening (expected FAIL): under the `import re as _re` alias, a group
read of an UNGUARDED match local is `None.group(1)` when the subject does not match (CPython
AttributeError), so the read carries the VC `handle <> 0`, which must NOT prove. Control: 9900.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re as _re

_KV = _re.compile(r"(\w+)=(\w+)")


#@ ensures \str_length(\result) >= 0
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
