from typing import List
_ = 0  # anchor


class MyList(list):
    pass


#@ ensures \result == 1
def probe() -> int:
    m = MyList()
    return len(m)
