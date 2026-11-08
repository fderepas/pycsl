r"""raise NotImplementedError under no_exception"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    raise NotImplementedError()


if __name__ == "__main__":
    print("CPython:", probe())
