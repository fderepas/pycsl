r"""Test 9910 -- lvS hval f-string CONTROL (expected PASS): `f"{fn}:{ln}"` over `.get` reads of a
`Dict[str, PyVal]` (hval values) IS a Python `str`: an `HStr s` segment is `s`, every other carrier
the program `val hval_fmt_other` (no `function`: `f"{True}"` and `f"{1}"` must not be equated), joined
by the length-exact `str_concat_op` (was the int-model `str_concat`, refused by R325). The literal ":"
makes `\str_length(\result) >= 1` provable. Twin: 9911 (must FAIL).
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \str_length(\result) >= 1
#@ assigns \nothing
def sel(loc: Dict[str, PyVal]) -> str:
    fn = loc.get("file-name")
    ln = loc.get("start-line")
    s = f"{fn}:{ln}"
    return s


if __name__ == "__main__":
    for d in [{"file-name": "a.mlw", "start-line": 3}, {}, {"file-name": True, "start-line": 1}]:
        r = sel(d)
        print("VIOLATION contract" if len(r) < 1 else "result", r)
