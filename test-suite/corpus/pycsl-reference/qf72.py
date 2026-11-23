# u72 helper (route #628, review rt80 R1c / R1d): a second library that defines its own `f`, returning 2.


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return 2
