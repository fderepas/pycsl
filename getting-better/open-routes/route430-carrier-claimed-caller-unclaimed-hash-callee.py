r"""OPEN ROUTE #430 carrier (probe l3d, executor rg 2026-10-28): a `no_exception \all` caller of an un-claimed callee that hashes `m.get("a")` PROVES; CPython raises TypeError. Gated by bin/check-open-route-carriers.py (SUCCESS today).
"""
from typing import Dict, Any

#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1

#@ no_exception \all
#@ ensures \result == 1
def caller(m: Dict[str, Any]) -> int:
    return h(m)

if __name__ == "__main__":
    print(caller({"a": [1]}))
