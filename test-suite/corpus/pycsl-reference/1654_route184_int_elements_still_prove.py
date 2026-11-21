r"""Test 1654 - ROUTE #184 control (gen #29): a list literal and a dict literal with ordinary int values are unchanged - `xs[0] == 1` and `d["a"] == 2` prove.
"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    xs: List[int] = [1]
    d: Dict[str, int] = {"a": 2}
    return xs[0] == 1 and d["a"] == 2
