r"""Test 7195 -- route #463 (expected PASS): CONTROL -- prose comments `# @dataclass` / `# @property` and a QUOTED directive `#     #@ ensures ...` are not near-misses. Every `#@` line is attached; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

# @dataclass would make this a record; @property too -- prose, not a directive.
#     #@ ensures \result == 0      <-- a quoted example, deliberately disabled
#@ ensures \result == n
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
