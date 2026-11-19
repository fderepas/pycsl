from collections import defaultdict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d = defaultdict(int)
    x = d[5]
    if 5 in d:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 0, f()
