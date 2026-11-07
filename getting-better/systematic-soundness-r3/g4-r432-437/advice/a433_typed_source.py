# advice probe (route #433): witness 6530 joining elements derived `str` (a display of `str` parameters)
#@ no_exception \all
def f(a: str, b: str) -> int:
    return len("".join([a, b]))
