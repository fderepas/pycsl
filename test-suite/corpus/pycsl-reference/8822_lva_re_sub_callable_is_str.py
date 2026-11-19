r"""Test 8822 -- lvA re.sub callable repl + compiled pattern (expected PASS): `p = re.compile(<literal>)`
bound once and `p.sub(<closed pure lambda>, <str>, count=1)` / `re.sub(<pat>, <closed pure lambda>, <str>)`
return a `str` (CPython: `re.sub` returns str or raises). They lower to the law-free PLAIN
`val re_sub_callable_op (pat s: string) : string`, so the results are strings and the `str` methods on
them are the faithful string ops: a `.strip()` result is never longer. At base the calls were opaque ints
(R325). Twin: 8823 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re


#@ ensures \result == True
#@ assigns \nothing
def expand(s: str) -> bool:
    p = re.compile(r"\(\s*_\s*:\s*([^()]+)\)\s*")
    t = p.sub(lambda m: f"{m.group(1).strip()} -> ", s, count=1)
    u = re.sub(r"\b(\w+)\s*<=\s*(\w+)", lambda m: f"{m.group(2)} >= {m.group(1)}"
               if not re.search(r"\bforall\b", m.group(1)) else m.group(0), t)
    return len(u.strip()) <= len(u)


if __name__ == "__main__":
    for s in ["(_ : b > 0) P", "a <= b", ""]:
        r = expand(s)
        print("VIOLATION contract" if r is not True else "result", r)
