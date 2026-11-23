# u61 witness 10343 (review rt74 V2D, the `import a.b` form): a dotted module import in an --import-path
# dependency.
import zpy61.b


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return zpy61.b.one()
