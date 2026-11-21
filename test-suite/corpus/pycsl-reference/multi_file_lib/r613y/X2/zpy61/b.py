# u61 witnesses 10340 / 10343 (review rt74 V2D): the `zpy61.b` pycsl verified against; CPython never loads
# it when the program's directory holds a regular package `zpy61`.


#@ ensures \result == 1
#@ assigns \nothing
def one() -> int:
    return 1
