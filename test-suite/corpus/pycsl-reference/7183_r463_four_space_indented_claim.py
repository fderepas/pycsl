r"""Test 7183 -- route #463 (expected FAIL): red-team 37 witness `e22_t100_four_space_indent` -- a 4-space-indented `#@` block above a column-0 `def` was dropped. PROVED at 33f7ac681 ("All contracts formally proven") while CPython breaks the written contract; now REFUSED (route #463, claim conservation).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

    #@ ensures \result == n
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
