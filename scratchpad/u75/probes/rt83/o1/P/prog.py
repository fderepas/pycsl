import unittest
import zv83o1.b


#@ ensures \result == 1
def g() -> int:
    return zv83o1.b.one()


print("result", g())
