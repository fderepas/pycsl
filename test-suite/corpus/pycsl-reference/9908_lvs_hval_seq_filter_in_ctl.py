r"""Test 9908 -- lvS hval-element filter CONTROL (expected PASS): `[r for r in parse(s) if "k" in r]`
over the `seq hval` result of a `-> List[Dict[str, PyVal]]` callee is the definitional fold
`hval_seq_filter_in "k" xs (Seq.length xs)` (a `let rec function`, no axiom, no assumed ensures; was
the int-typed `list_content_comp_N : array int -> array int`, a Why3 type error). The function
verifies with its `\result`-free contract. Twin: 9909 (must FAIL).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List

PyVal = Any


#@ \trusted
#@ assigns \nothing
def parse(s: str) -> List[Dict[str, PyVal]]:
    return [{"k": 1}, {"j": 2}] if s else []


#@ assigns \nothing
def keep(s: str) -> List[Dict[str, PyVal]]:
    return [r for r in parse(s) if "k" in r]


if __name__ == "__main__":
    print("result", keep("x"), keep(""))
