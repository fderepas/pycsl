r"""Test 9999 -- route #603 control (expected PASS): witness 9974's helper called from a function with NO no_exception claim -- the laundering rule is claim-gated (a TypeError is an exceptional exit, which partial correctness admits), and a length is non-negative on every normal return
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ assigns \nothing
def name(d: Dict[str, PyVal]) -> str:
    return d.get("name") or "anon"


#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return len(name(d))


if __name__ == "__main__":
    print("result", f({"name": "ab"}))
    try:
        f({"name": 5})
    except TypeError:
        print("TypeError (exceptional exit, admitted without a claim)")
