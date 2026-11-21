#@ no_exception \all
def f(s: str, n: int) -> int:
    return len(s.split(" ", maxsplit=n))
