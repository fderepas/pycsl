# u61 witness 10340 (review rt74 V2D): a dotted absolute import in an --import-path dependency.
from zpy61.b import one


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return one()
