import time
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if time.time() % 1 == 0 or True:
        pass
    t = time.time()
    if t // 1 == t:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
