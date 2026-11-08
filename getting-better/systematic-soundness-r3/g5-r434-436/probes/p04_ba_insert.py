#@ no_exception \all
def f(n: int) -> int:
    b = bytearray(2)
    b.insert(n, 3)
    return len(b)
