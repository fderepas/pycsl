# Advice probe (route #453, module attribute): witness 6862 with the module's actual name (`sys.maxsize`).
import sys


#@ no_exception \all
def f(n: int) -> int:
    y = sys.maxsize
    return n
