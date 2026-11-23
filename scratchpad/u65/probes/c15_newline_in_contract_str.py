#@ requires x > 0 and x < 0 and s != "a\n  end\nfunction=b"
#@ ensures \result == 99
def f(x: int, s: str) -> int:
    return 1
