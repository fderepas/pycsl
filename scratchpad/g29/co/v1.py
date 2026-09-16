r"""G29 CO-V1 — route #159 POSITIVE control (str): an in-range index under no_exception IndexError must still prove."""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    s = "abc"
    return 1 if s[1] == "b" else 0
