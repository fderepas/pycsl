from typing import List
_ = 0  # anchor


class MyList(list):
    pass


#@ ensures \result == 0
def probe() -> int:
    m = MyList()
    return len(m)
