r"""Test 9894 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): the same SCHEMA-TYPED LIST slot hashed with NO claim: a value the schema derives a list is statically unhashable, so it is denied UNCONDITIONALLY (PYCSL-R349-UNHASHABLE-RECORD; admitted at base as an underivable, ambient value). CPython raises TypeError.
"""
# pycsl-expected: FAIL
from typing import List, Set, TypedDict


class R(TypedDict):
    name: str
    tags: List[str]


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
        print("VIOLATION: TypeError")
