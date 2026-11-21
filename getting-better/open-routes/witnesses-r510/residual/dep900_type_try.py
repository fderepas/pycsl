#@ ensures \result == n
def g(n: int) -> int:
    return n


try:
    type g = int
except Exception:
    pass
