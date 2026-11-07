r"""exception group of handlers order with subclass first"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    try:
        raise KeyError()
    except KeyError:
        return 1
    except LookupError:
        return 2


if __name__ == "__main__":
    print("CPython:", probe())
