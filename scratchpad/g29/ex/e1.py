r"""exception variable args read"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        raise ValueError(5)
    except ValueError as e:
        return len(e.args)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
