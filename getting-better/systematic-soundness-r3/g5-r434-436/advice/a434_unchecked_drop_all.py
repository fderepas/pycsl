# advice of PYCSL-R434-UNCHECKED-SITE followed for witness 6570 (x01): drop \all
#@ no_exception IndexError
def f(ws: list[str]) -> int:
    xs = [ord(w) for w in ws]
    return 0
