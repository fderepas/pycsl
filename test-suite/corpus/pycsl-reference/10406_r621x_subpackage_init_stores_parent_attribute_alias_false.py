r"""Test 10406 -- run #9 u69, review rt78 t8, route #621 extended (FAIL, PRE-EXISTING). The package zs06's
__init__ loads its submodule b, then its sub-package zs06.sub, whose __init__ stores the sibling module c
into the PARENT package's attribute through an alias: `import zs06 as _p; _p.b = c0`. `zs06.b.one()` then
runs c.one(): `cd <tree root> && python <this file>` prints "result 2". pycsl lowered `zs06.b.one` to
zs06/b.py's contract and PROVED the claim below (base c115e0a5a and u66 b95cb8767). REFUSED:
PYCSL-SEM-IMPORT-PACKAGE-SUBMODULE-REBOUND.
"""
# pycsl-expected: FAIL
import zs06.b


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return zs06.b.one()


if __name__ == "__main__":
    print("result", g())
