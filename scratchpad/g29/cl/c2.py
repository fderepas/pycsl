r"""closure over loop variable late binding"""
from typing import List, Dict, Callable
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    fs: List[Callable[[], int]] = []
    for i in range(3):
        fs.append(lambda: i)
    return fs[0]()


if __name__ == "__main__":
    print("CPython:", probe())
