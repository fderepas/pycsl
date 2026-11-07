#@ ensures True
def f(x: str) -> int:
    s = x + "b"
    return len(s)
