r"""Test 8905 -- lvC wall-2 walker (expected FAIL): false twin of 8904. The leaf now REQUIRES something
of the sub-dict it is handed (no `"type"` key); the walker calls it only on a dict whose `"type"` is
`"Subscript"`, so the precondition is violated in CPython. The walker supplies the leaf an
ARBITRARY `any <T>` value, so the call's precondition VC must stay unprovable.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import warnings


#@ requires not ("type" in sub)
#@ assigns \nothing
def check_leaf(sub: dict, tags: set, fname: str) -> None:
    idx = sub.get("index", {})
    if not (isinstance(idx, dict) and idx.get("type") == "String"):
        warnings.warn(f"Function '{fname}': index is not a string literal")


#@ assigns \nothing
def walk(stmts: list, tags: set, fname: str) -> None:
    for s in stmts:
        if not isinstance(s, dict):
            continue
        for k, v in s.items():
            if k == "value" and isinstance(v, dict) and v.get("type") == "Subscript":
                check_leaf(v, tags, fname)
            elif isinstance(v, dict):
                if v.get("type") == "Subscript":
                    check_leaf(v, tags, fname)
                walk([v], tags, fname)
            elif isinstance(v, list):
                walk(v, tags, fname)


if __name__ == "__main__":
    v = {"type": "Subscript", "index": {"type": "Number"}}
    print("VIOLATION requires" if "type" in v else "result", sorted(v))
