r"""Test 9902 -- lvS cap-re-gate-widening (expected FAIL): under the `import re as _re` alias,
`m.group(3)` on a 2-group pattern raises IndexError in CPython (the group count is computed by
CPython's own parser), so the read lowers to a failing `assert false` VC. Control: 9900.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re as _re

_KV = _re.compile(r"(\w+)=(\w+)")


#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def third(s: str) -> str:
    m = _KV.match(s)
    if m:
        return m.group(3)
    return ""


if __name__ == "__main__":
    try:
        third("a=b")
        print("result ok")
    except IndexError:
        print("VIOLATION IndexError")
