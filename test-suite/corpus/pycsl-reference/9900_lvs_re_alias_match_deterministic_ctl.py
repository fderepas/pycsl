r"""Test 9900 -- lvS cap-re-gate-widening CONTROL (expected PASS): the lvO re.Match model now also
applies when the module binds the stdlib `re` under ONE alias (`import re as _re`, no plain `import
re`, the alias bound nowhere else) and the compiled pattern is `_re.compile(<literal>)` AFTER the
import. Two match locals of the same constant on the same subject read the same group (the law-free
model's determinism, exact since a match local never escapes). Twins: 9901 / 9902 / 9903 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re as _re

_KV = _re.compile(r"(\w+)=(\w+)")


#@ ensures \result == True
#@ assigns \nothing
def same_key(s: str) -> bool:
    m = _KV.match(s)
    n = _KV.match(s)
    if m:
        if n:
            return m.group(1) == n.group(1)
        return False
    return True


if __name__ == "__main__":
    for s in ["a=b", "key=val", "", "=x", "x"]:
        r = same_key(s)
        print("VIOLATION contract" if r is not True else "result", r)
