from collections import defaultdict

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    d = defaultdict(int, {1: 5})
    if d[1] == 0:
        return 7
    return 0
