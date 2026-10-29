r"""Test 7021 -- route #452 (expected FAIL): red-team 36 probe c14_y021_realistic_count -- `payload.count(code)` (CPython ValueError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(code: int) -> int:
    payload = b'a\nb\n'
    return payload.count(code)


if __name__ == "__main__":
    try:
        r = f(-1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
