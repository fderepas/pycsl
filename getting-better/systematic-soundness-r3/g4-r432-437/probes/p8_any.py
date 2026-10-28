from typing import Any
#@ no_exception \all
def f(x: Any) -> int:
    return len(x.strip())
