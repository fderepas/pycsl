r"""Test 2458 — route #251 (expected FAIL): Contract side: `ensures x <= x` on `x: Any` PROVED. CPython: `nan <= nan` is
False — no user class needed.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures x <= x
#@ assigns \nothing
def f(x: Any) -> int:
    return 0


if __name__ == "__main__":
    x = float("nan")
    assert not (x <= x)
