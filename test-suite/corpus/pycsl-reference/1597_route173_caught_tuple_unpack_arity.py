r"""Test 1597 - ROUTE #173 (gen #29): the same unpack inside `try ... except ValueError: return 9` PROVED `\result == 0` (CPython 9) - route #171 widens the context, and now the unpack is refused there too.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s = "a"
    try:
        a, b = s.split(",")
    except ValueError:
        return 9
    return 0
