r"""ghost assignment affecting real control flow"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    x = 0
    #@ ghost x = 1
    return x


if __name__ == "__main__":
    print("CPython:", probe())
