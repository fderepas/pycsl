from typing import Optional
#@ no_exception AttributeError
def f(x: Optional[str]) -> int:
    return len(x.strip())
