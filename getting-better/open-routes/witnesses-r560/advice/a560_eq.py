# advice probe (route #560): witness g1419/dt1200 comparing the member as an int, `k == IE.B`.
import enum


class IE(enum.IntEnum):
    A = 1
    B = 2


#@ no_exception \all
def f(k: int) -> int:
    return 1 if k == IE.B else 0
