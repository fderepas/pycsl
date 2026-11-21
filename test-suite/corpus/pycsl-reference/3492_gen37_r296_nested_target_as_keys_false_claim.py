r"""Test 3492 — gen #37 route #296 (expected FAIL): a NESTED loop over a pyval loop target (`for row in d["rows"]: for x in row`): `row` is an
`hval` element, iterated bare -> the key arm. CPython: False.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def first_is_str(d: Dict[str, PyVal]) -> bool:
    for row in d["rows"]:
        for x in row:
            return isinstance(x, str)
    return True

if __name__ == "__main__":
    print(first_is_str({"rows": [[1]]}))
