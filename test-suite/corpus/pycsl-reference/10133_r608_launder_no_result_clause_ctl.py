r"""Test 10133 -- run #8 batch B, R2 over-refusal CONTROL (expected PASS): the same laundering function with no `\result` clause: not refused by PYCSL-R608-LAUNDER-OWN-RESULT-CLAUSE, the frame proves (hoare) as at base.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ assigns \nothing
def name(d: Dict[str, PyVal]) -> str:
    return d.get("a") or "z"

if __name__ == "__main__":
    print("result", name({"a": [1]}))
