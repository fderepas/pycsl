r"""Test 5362 -- gen #37 route #383 (expected FAIL): module alias `DD = D`, `d: DD`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any

@dataclass
class D:
    x: int

DD = D

#@ no_exception \all
#@ ensures \result == 1
def g(d: DD) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
