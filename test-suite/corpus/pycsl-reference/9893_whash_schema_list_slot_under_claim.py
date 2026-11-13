r"""Test 9893 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): a SCHEMA-TYPED LIST slot -- `r["tags"]` of a file TypedDict declaring `tags: List[str]` -- hashed under `no_exception \all`: the schema derives it a list, so it is DENIED (PYCSL-R349-UNHASHABLE-RECORD; at base route R-gate refused it as underivable). CPython raises TypeError.
"""
# pycsl-expected: FAIL
from typing import List, Set, TypedDict


class R(TypedDict):
    name: str
    tags: List[str]


#@ no_exception \all
#@ ensures \result == n + 1
def f(r: R, n: int) -> int:
    seen: Set[str] = set()
    if r["tags"] in seen:
        return n + 1
    return n + 1


if __name__ == "__main__":
    try:
        print(f({"name": "a", "tags": ["t"]}, 0))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
