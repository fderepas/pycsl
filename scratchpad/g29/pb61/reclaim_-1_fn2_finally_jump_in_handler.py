from typing import List
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    xs: List[int] = [0]
    try:
        raise ValueError()
    except ValueError:
        return xs[0]
    finally:
        xs[0] = 9
