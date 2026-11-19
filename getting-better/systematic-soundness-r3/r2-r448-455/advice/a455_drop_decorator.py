# advice probe (route #455): witness 6966 with the decorator dropped -- must VERIFY
def size(p: str) -> int:
    return len(p)


#@ no_exception \all
def f(path: str) -> int:
    return size(path)
