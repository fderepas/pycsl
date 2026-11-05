r"""Test 8904 -- lvC wall-2 walker with a VERIFIED leaf (expected PASS). The void `.items()`-walk `walk`
lowers onto the certified pyval/pydict catamorphism and hands its leaf an arbitrary well-typed value
`any <T>` for the matched sub-dict (the leaf requires nothing of it). `<T>` must be the type the leaf's
`sub` parameter is EMITTED at: a leaf whose body reads `sub.get("<str>")` is string-keyed
(`map string (option int)`). At base the walker hard-coded `map int (option int)` (right only for a
`\trusted` stub leaf) and the file failed the Why3 type-check. Twin: 8905 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import warnings


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
    walk([{"value": {"type": "Subscript", "index": {"type": "Number"}}}], set(), "f")
    print("result ok")
