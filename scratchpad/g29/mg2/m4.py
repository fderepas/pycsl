r"""module global conditional definition"""
from typing import List, Dict
_ = 0  # anchor


FLAG = False
if FLAG:
    K = 1
else:
    K = 2


#@ ensures \result == 1
def probe() -> int:
    return K


if __name__ == "__main__":
    print("CPython:", probe())
