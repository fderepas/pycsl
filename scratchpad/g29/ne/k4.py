r"""G29 NE-K4 — route #160 control: a non-raising use under no_exception ValueError is NOT refused."""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    s = "a b"
    return len(s.split(" "))
