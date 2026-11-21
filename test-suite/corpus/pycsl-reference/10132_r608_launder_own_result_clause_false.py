r"""Test 10132 -- run #8 batch B, u48 rule R2 narrowed (expected FAIL): a LAUNDERING function (`return d.get("a") or "z"` under `-> str`) whose OWN clause decides a str-only fact of `\result` (`\result * 0 == ""`; route #608 residual q06): CPython returns `[1]` for {"a": [1]} and `[1] * 0 == []`. REFUSED: PYCSL-R608-LAUNDER-OWN-RESULT-CLAUSE.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result * 0 == ""
#@ assigns \nothing
def name(d: Dict[str, PyVal]) -> str:
    return d.get("a") or "z"

if __name__ == "__main__":
    r = name({"a": [1]})
    print("VIOLATION contract" if r * 0 != "" else "result", r)
