r"""control: present index in try with IndexError handler"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    xs: List[int] = [1, 2]
    try:
        v = xs[1]
    except BaseException:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
