#@ no_exception \all
def f(n: int) -> int:
    xs = [1, 2]
    xs.insert(n, 3)
    return len(xs)
