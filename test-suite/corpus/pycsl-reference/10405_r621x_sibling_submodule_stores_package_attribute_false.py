r"""Test 10405 -- run #9 u69, review rt78 t4, route #621 extended (FAIL, PRE-EXISTING). The package zs05's
__init__ imports its submodule d, which loads zs05.b and then STORES the sibling module c into the package
attribute: `import zs05; zs05.b = c0`. `import zs05.b` finds zs05.b in sys.modules and does not reset the
attribute, so `zs05.b.one()` runs c.one(): `cd <tree root> && python <this file>` prints "result 2". pycsl
lowered `zs05.b.one` to zs05/b.py's contract and PROVED the claim below (base c115e0a5a and u66 b95cb8767:
route #621 judged only Name bindings of package __init__s). REFUSED: PYCSL-SEM-IMPORT-PACKAGE-SUBMODULE-REBOUND.
"""
# pycsl-expected: FAIL
import zs05.b


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return zs05.b.one()


if __name__ == "__main__":
    print("result", g())
