from json import JSONDecodeError
K = JSONDecodeError


#@ no_exception \all
def f() -> int:
    s = {K}
    return len(s)
