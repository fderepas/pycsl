"""Advice probe (route #554, PYCSL-R554-IMPORTED-CALL-SIGNATURE): 'Call the function or class with exactly
its parameters' -- witnesses g1319_bt1200 / bt1204 / bt1210 with `g(k)` and `DC(k)`. VERIFIES under
`no_exception \\all`."""
from rt52dep2 import DC, g


#@ no_exception \all
def f(k: int) -> int:
    c = DC(k)
    return g(k)


if __name__ == "__main__":
    print("result", f(1))
