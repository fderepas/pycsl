r"""Test 9892 -- W-hash (dict-value-model-r4 §2.5, expected PASS): CONTROL: a SCHEMA-TYPED SCALAR slot -- `r["name"]` of a file TypedDict whose own body declares `name: str` -- hashed under `no_exception \all` (a membership test, a dict-key store) is DERIVED hashable from the schema and admitted; both PROVE. REFUSED at base by route R-gate (the slot read was underivable).
"""
# pycsl-expected: PASS
from typing import Dict, List, Set, TypedDict


class R(TypedDict):
    name: str
    tags: List[str]


#@ no_exception \all
#@ ensures \result == n + 1
def f(r: R, n: int) -> int:
    seen: Set[str] = set()
    if r["name"] in seen:
        return n + 1
    return n + 1


#@ no_exception \all
#@ ensures \result == n + 1
def g(r: R, n: int) -> int:
    d: Dict[str, int] = {}
    d[r["name"]] = 1
    return n + 1


if __name__ == "__main__":
    r: R = {"name": "a", "tags": ["t"]}
    print(f(r, 0), g(r, 0))
