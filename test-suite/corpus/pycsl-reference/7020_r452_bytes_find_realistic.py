r"""Test 7020 -- route #452 (expected FAIL): red-team 36 probe c14_y020_realistic_header -- `data.find(sep)` on a local bytes (CPython ValueError for sep = 0x100). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(sep: int) -> int:
    data = b'GET / HTTP/1.1'
    return data.find(sep)


if __name__ == "__main__":
    try:
        r = f(0x100)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
