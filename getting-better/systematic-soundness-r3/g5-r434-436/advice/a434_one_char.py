# advice of PYCSL-R434-ORD-LENGTH followed for witness 6552 (or1): pass a one-character str
#@ no_exception \all
def f(s: str) -> int:
    return ord("ab"[0])
