r"""Test 9846 — dict-value-model-r4 key canonicalisation (expected FAIL): `{1: "a", True: "b"}` is ONE key in CPython (`len == 1`); a nested PyVal dict is keyed by `str` (HVAL-STR-KEYS), so the int / bool keyed literal is not representable and the (false) `len == 2` claim is refused at the type check, never proved. `hval_canon` (certified `eq_canon_coherent`) serves the hashed-key positions (W-hash).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {1: "a", True: "b"}}
    return len(d.get("m"))
