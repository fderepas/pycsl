from collections import defaultdict
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = defaultdict(lambda: 7)
    if d[5] == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
