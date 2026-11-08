r"""Test 3552 — gen #37 route #298 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION HVAL-STR-KEYS).

Program: `for k, v in d.get("xs", {}).items(): return isinstance(k, str)` with `ensures \result == True`. The `hval` model keys every NESTED dict by `string` (`HMap` over `hpairs`), so
the `.items()` key is a `str` symbol and the claim PROVES; CPython REFUTES it (see `__main__`: a nested dict may have an int key,
`Dict[str, PyVal]` constrains only the top-level keys). This is NOT a soundness bug of the default
mode: it is the counterexample of the declared assumption HVAL-STR-KEYS, which
`pycsl --soundness-report` lists for this file and the reference docs state. Twin 3556 runs the
same program under `--strict-hval-keys`, where the assumption is dropped and the claim FAILS.
"""
# pycsl-model-assumption: HVAL-STR-KEYS
# pycsl-expected: PASS

from typing import Any, Dict

PyVal = Any


#@ ensures \result == True
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> bool:
    for k, v in d.get("xs", {}).items():
        return isinstance(k, str)
    return True


if __name__ == "__main__":
    print(f({"xs": {1: 2}}))  # False: the nested key is the int 1
