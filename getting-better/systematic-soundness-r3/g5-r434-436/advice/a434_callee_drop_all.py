# advice of PYCSL-R434-CALLEE-UNCHECKED-SITE followed for witness 6572 (x05): drop \all from the caller
def h(s: str) -> int:
    return ord(s)


#@ no_exception IndexError
def f(s: str) -> int:
    return h(s)
