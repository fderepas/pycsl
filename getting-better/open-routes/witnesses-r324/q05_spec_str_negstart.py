#@ requires len(s) == 3
#@ ensures \result == len(s[-2:3])
#@ assigns \nothing
def f(s: str) -> int:
    return 0

if __name__ == "__main__":
    assert f("abc") == len("abc"[-2:3]), f("abc")
