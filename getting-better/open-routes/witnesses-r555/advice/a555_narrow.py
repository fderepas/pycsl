"""Advice probe (route #555, PYCSL-R555-IMPORTED-NONE-RESULT): 'Bind the result to a name and narrow it
first' -- witness g1327_cb1200 (`gopt(k) + 1`) with `v = gopt(k); if v is None: return 0`. VERIFIES under
`no_exception \\all`."""
from rt52dep5 import gopt


#@ no_exception \all
def f(k: int) -> int:
    v = gopt(k)
    if v is None:
        return 0
    return v + 1


if __name__ == "__main__":
    print("result", f(1), f(-2))
