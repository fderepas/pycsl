#@ no_exception \all
def f(n: int) -> int:
    xs = [1, 2]
    xs.pop(n)
    return len(xs)
