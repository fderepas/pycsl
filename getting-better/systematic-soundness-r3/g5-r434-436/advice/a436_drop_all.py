# advice of PYCSL-R436-SSIZE-ARGUMENT followed for witness 6577 (x07): drop \all
#@ ensures \result == n
#@ no_exception \all
def g(n: int) -> int:
    return n


#@ no_exception IndexError
def f(s: str, n: int) -> int:
    return len(s.split(" ", g(n)))
