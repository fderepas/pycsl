from typing import Optional
#@ no_exception \all
def f(x: "Optional[str]") -> int:
    return len(x.strip())
