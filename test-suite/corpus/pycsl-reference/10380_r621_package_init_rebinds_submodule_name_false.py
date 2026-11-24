r"""Test 10380 -- run #9 u66, review rt76 r2, route #621 (FAIL, PRE-EXISTING). The program's directory holds
the package zr80 whose __init__ does `from . import b as b0; from . import c as b`: it loads the submodule
zr80.b first and then binds the NAME `b` to the sibling module c. `import zr80.b` finds zr80.b in
sys.modules and does not reset the attribute, so `zr80.b.one()` runs c.one(): `cd <tree root> && python
<this file>` prints "result 2". pycsl lowered `zr80.b.one` to zr80/b.py's contract and PROVED the claim
below (base 2873a902d). REFUSED: PYCSL-SEM-IMPORT-PACKAGE-SUBMODULE-REBOUND.
"""
# pycsl-expected: FAIL
import zr80.b


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return zr80.b.one()


if __name__ == "__main__":
    print("result", g())
