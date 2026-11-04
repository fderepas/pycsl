# advice probe (route #556): witness g1415/dp1220 searching a str parameter, `"a" in t`.


#@ no_exception \all
def f(k: int, t: str) -> int:
    return 1 if "a" in t else 0
