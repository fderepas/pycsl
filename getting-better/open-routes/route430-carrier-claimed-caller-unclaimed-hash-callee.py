r"""OPEN ROUTE #430 carrier (probe l3d, executor rg 2026-10-28): a `no_exception \all` caller of an un-claimed callee that hashes `m.get("a")` PROVED (before the repair); CPython raises TypeError. CLOSED by the route #430 repair (executor h430, 2026-10-28): now REFUSED (PYCSL-R430-CALLEE-UNDERIVABLE-HASH); bin/check-open-route-carriers.py asserts REFUSED.
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
