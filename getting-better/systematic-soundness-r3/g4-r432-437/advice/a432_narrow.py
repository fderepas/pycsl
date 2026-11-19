# advice probe (route #432): witness 6500 with the receiver narrowed first, as the message says
from typing import Optional


#@ no_exception \all
def f(x: Optional[str]) -> int:
    if x is not None:
        return len(x.strip())
    return 0
