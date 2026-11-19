r"""G29 NE-K2 — route #160 control: a non-raising use under no_exception ZeroDivisionError is NOT refused."""
from typing import List
_ = 0  # anchor


#@ no_exception ZeroDivisionError
def probe() -> int:
    return pow(2, 3)
