from collections import Counter

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = Counter()
    if c[1] == 0:
        return 7
    return 0
