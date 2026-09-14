"""ROUTE #107-A EXPLOIT, MINIMAL — identical to a_ctl2 except the else block also binds a
local whose NAME contains "raise". That single identifier deletes the whole else block.
"""
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    y = 0
    try:
        y = 1
    except ValueError:
        y = 9
    else:
        y = 5
        praiseworthy = 0
    return y
