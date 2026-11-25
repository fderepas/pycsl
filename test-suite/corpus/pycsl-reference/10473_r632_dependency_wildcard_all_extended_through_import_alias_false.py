r"""Test 10473 -- run #9 u73, review rt81 x4, route #632 (FAIL, PRE-EXISTING). The dependency zu73j does
`from zu73k import *`; zu73k/__init__.py has the literal `__all__ = ["k"]` and imports its submodule k,
which does `from . import __all__ as A; A.append("w")`: the list is extended in place through an import
alias, so CPython's wildcard also LOADS zu73k/w.py, whose import-time `zu73i.one = _two` makes `cd <tree
root> && python <this file>` print "result 5". L19 c115e0a5a and 08e65645c PROVED the claim below. REFUSED:
PYCSL-SEM-IMPORT-WILDCARD-ALL-UNKNOWN (u73: an import alias naming `__all__` is an outside mention).
"""
# pycsl-expected: FAIL
import zu73i
from zu73j import three


#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    return zu73i.one() + three()


if __name__ == "__main__":
    print("result", g())
