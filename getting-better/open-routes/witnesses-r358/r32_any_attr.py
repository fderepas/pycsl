# route #343: attribute read on `x: Any`
from typing import Any

#@ no_exception \all
def f(x: Any) -> int:
    y = x.foo
    return 0

if __name__ == "__main__":
    f(1)
