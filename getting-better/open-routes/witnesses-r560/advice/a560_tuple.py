# advice probe (route #560): witness g1419/dt1200 searching the members, `k in (IE.A, IE.B)`.
import enum


class IE(enum.IntEnum):
    A = 1
    B = 2


#@ no_exception \all
def f(k: int) -> int:
    return 1 if k in (IE.A, IE.B) else 0
