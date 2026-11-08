from collections import Counter
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = Counter(a=5)
    if c["a"] == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
