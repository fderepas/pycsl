r"""Test 3554 — gen #37 route #298 (expected FAIL): `--strict-hval-keys` drops HVAL-STR-KEYS.

Same program as 3550: `xs = d["xs"]; for k, v in xs.items(): return isinstance(k, str)` with `ensures \result == True`. Under the flag the key of a nested dict binds the UNINTERPRETED
`hval_keys_hget` (an `hval` of unknown carrier, no axiom), never a `string` / `HStr`, so the claim,
FALSE in CPython, no longer proves.
"""
# pycsl-flags: --strict-hval-keys
# pycsl-expected: FAIL

from typing import Any, Dict

PyVal = Any


#@ ensures \result == True
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> bool:
    xs = d["xs"]
    for k, v in xs.items():
        return isinstance(k, str)
    return True


if __name__ == "__main__":
    print(f({"xs": {1: 2}}))  # False: the nested key is the int 1
