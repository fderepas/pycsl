#@ requires n > 0
#@ ensures \result == 1
#@ assigns \nothing
def g(n: int) -> int:
    return 1

#@ requires True
#@ raises ValueError when True
#@ assigns \nothing
def f() -> int:
    raise ValueError("x") from g(0)
