# u61 witnesses 10340 / 10343 (review rt74 V2D): the `zpy61.b` CPython runs (through zpy61/__init__.py).
print("PROGRAM-DIR zpy61_alt/b.py loaded:", __file__)


#@ ensures \result == 2
#@ assigns \nothing
def one() -> int:
    return 2
