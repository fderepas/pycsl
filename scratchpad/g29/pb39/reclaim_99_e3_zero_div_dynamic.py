_ = 0  # anchor


#@ no_exception ZeroDivisionError
#@ ensures \result == 99
def probe(d: int) -> int:
    return (10 // d) * 0
