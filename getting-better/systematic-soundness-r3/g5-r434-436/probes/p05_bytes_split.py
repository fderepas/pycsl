#@ no_exception \all
def f(b: bytes, n: int) -> int:
    return len(b.split(b" ", n))
