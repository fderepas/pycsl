#@ requires True
#@ ensures True
def f(s: str) -> str:
    return s.strip()

#@ requires True
#@ ensures True
def g(s: str) -> str:
    t = s.strip()
    return t

#@ requires True
#@ ensures True
def h(parts: str) -> int:
    if parts.strip():
        return 1
    return 0
