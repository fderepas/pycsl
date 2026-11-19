from typing import Optional
def g(k: int) -> Optional[str]:
    return None
#@ no_exception \all
def f(k: int) -> int:
    return len(g(k).strip())
