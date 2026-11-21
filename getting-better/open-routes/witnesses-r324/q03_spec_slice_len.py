#@ requires len(s) == 3
#@ ensures \result == len(s[1:-1])
#@ assigns \nothing
def f(s: str) -> int:
    return 0

if __name__ == "__main__":
    assert f("abc") == len("abc"[1:-1]), f("abc")
