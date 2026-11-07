r"""Test 7036 -- route #459 (expected FAIL): red-team 36 probe c33_g013_if_type_checking -- `G` bound only under `if TYPE_CHECKING:` (CPython NameError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
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
