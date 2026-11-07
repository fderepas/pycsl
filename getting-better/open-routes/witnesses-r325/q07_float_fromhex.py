#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = float.fromhex("0x1.8p0")
    if x % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
