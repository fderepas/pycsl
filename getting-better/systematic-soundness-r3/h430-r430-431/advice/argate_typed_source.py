# Advice probe for PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM: witnesses 6470 / 6473 with the hashed
# value derived from a source declared with a hashable type (`Dict[str, str]` values, a `List`
# of `Dict[str, int]`). Expected: VERIFIES.
from typing import Dict, List


#@ no_exception \all
#@ ensures \result == 1
def f(m: Dict[str, str]) -> int:
    s = {m.get("a")}
    return 1


#@ no_exception \all
#@ ensures \result == 1
def names(funcs: List[Dict[str, int]]) -> int:
    seen = set()
    for g in funcs:
        seen.add(g.get("name"))
    return 1


if __name__ == "__main__":
    print(f({"a": "x"}), names([{"name": 1}]))
