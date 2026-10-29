r"""Test 7038 -- route #459 (expected FAIL): red-team 36 probe c33_g002_platform_cond -- `G` bound only under `if sys.platform == ..:` (CPython NameError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import sys
if sys.platform == 'nope':
    G = 1



#@ no_exception \all
def f(n: int) -> int:
    return G + n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
