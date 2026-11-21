#@ no_exception \all
def f(s: str, n: int) -> int:
    return len(s.replace("a", "b", n))
