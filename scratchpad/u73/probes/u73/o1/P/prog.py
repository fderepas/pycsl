from typing import List
import zv83o1.b


#@ ensures \result == 1
def g(xs: List[int]) -> int:
    return zv83o1.b.one()


print("result", g([1]))
