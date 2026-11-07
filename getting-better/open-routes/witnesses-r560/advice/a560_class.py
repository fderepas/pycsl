# advice probe (route #560): witness g1419/dt1202 iterating the class itself, `for m in IE`.
import enum


class IE(enum.IntEnum):
    A = 1
    B = 2


#@ no_exception \all
def f(k: int) -> int:
    c = 0
    for m in IE:
        c += 1
    return c
