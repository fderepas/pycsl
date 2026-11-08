from collections import OrderedDict
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = OrderedDict(a=5)
    if d["a"] == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
