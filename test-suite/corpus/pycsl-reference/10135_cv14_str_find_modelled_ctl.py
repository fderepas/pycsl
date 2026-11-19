r"""Test 10135 -- run #8 batch B, R4 over-refusal CONTROL (expected PASS): `x.find("a")` (modelled) with `ensures \result >= -1`: not refused by PYCSL-CV14-STR-RFIND-RECEIVER-DROPPED, proves x3 as at base.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple

#@ ensures \result >= -1
#@ assigns \nothing
def f(x: str) -> int:
    return x.find("a")

if __name__ == "__main__":
    print("result", f("ba"))
