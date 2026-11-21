r"""Test 3280 — gen #37 dict-value-wall Step 0, R5 (expected FAIL): red-team round 7 p081. The
receiver-form defaulted read `(rec.get("p") or {}).get("answer", "")` lowered to
`match <recv> with HMap m -> pairs_get m k ... | _ -> D`, so a NON-MAP truthy receiver answered the
default `D`. CPython: `(x or {})` is `{}` only when `x` is falsy; a truthy non-dict `x` (here `5`)
has no `.get` and raises AttributeError. Under `no_exception \all` the claim is FALSE
(`answer({"p": 5})` raises), and it PROVED in land27. Now the receiver-form `.get` asserts, in a
`no_exception` context covering AttributeError, that the receiver is a map: unprovable here.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "" or \result != ""
#@ assigns \nothing
#@ no_exception \all
def answer(rec: Dict[str, PyVal]) -> str:
    return (rec.get("p") or {}).get("answer", "") or ""


if __name__ == "__main__":
    try:
        answer({"p": 5})
        print("no exception")
    except AttributeError as e:
        print("AttributeError:", e)
