#@ requires x > 0 and x < 0 and s != """a
  end
b"""
#@ ensures \result == 99
def f(x: int, s: str) -> int:
    return 1
