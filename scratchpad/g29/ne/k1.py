r"""G29 NE-K1 — route #160 control: a non-raising use under no_exception ValueError is NOT refused."""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    t = 0
    for i in range(0, 5, 2):
        t = t + 1
    return t
