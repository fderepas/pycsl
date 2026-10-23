from collections import defaultdict

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    d = defaultdict(int)
    if d[9] == 0:
        return 7
    return 0
