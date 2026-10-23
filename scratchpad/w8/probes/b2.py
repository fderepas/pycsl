#@ requires True
#@ raises ValueError when True
#@ assigns \nothing
def g(n: int) -> int:
    raise ValueError("x")

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def driver() -> int:
    try:
        v: int = g(1)
        return 1
    except Exception:
        return 2
