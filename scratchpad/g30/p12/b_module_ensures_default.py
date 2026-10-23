#@ requires True
#@ ensures \result == k
def f(k: int = 5) -> int:
    return k


#@ ensures \result == 99
def probe() -> int:
    k = 99
    return f()
