from typing import List


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1]
    try:
        pass
    finally:
        xs[0] = 2
    return xs[0]
