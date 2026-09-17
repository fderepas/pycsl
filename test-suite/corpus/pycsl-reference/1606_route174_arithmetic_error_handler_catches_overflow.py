r"""Test 1606 - ROUTE #174 carrier (gen #29): `try: f = float(10 ** 400) except ArithmeticError: return 9; return 0` PROVED `\result == 0` on the #174 draft (CPython 9): ArithmeticError covers the modelled ZeroDivisionError, so the handler was accepted, but it also catches the unmodelled OverflowError. Every builtin subclass of a handler class must now be modelled, below a modelled class, or explicitly raised.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        f = float(10 ** 400)
    except ArithmeticError:
        return 9
    return 0
