"""ROUTE #107-A CONTROL — byte-for-byte the same shape with NO "raise" substring anywhere.
The else block must SURVIVE, so `\result` is 5 and `ensures \result == 1` must FAIL.
This is the control that shows the exploit's PROOF is caused by the substring and not by
the postcondition being provable anyway.
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
    return y
