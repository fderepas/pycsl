# advice probe (route #440): 6651 with the receiver declared `n: str` (a class with `upper` in the table) -> VERIFIES
#@ no_exception \all
def f(n: str) -> int:
    return len(n.upper())
