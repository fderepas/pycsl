# u72 helper (route #628, review rt80 R1): the ORIGIN of a re-exported function. Its `f` returns 1.


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1
