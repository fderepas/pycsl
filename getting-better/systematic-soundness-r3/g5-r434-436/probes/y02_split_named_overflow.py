#@ no_exception OverflowError
def f(s: str, n: int) -> int:
    return len(s.split(" ", n))
