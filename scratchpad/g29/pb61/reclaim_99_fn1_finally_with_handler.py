from typing import List
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    xs: List[int] = [0]
    try:
        return xs[0]
    except ValueError:
        return 1
    finally:
        xs[0] = 9
