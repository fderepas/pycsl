from collections import OrderedDict

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    d = OrderedDict([(1, 5)])
    if d[1] == 0:
        return 7
    return 0
