import hw83q4
import zf83q4
from dp83q4 import three


#@ ensures \result == 4
def g() -> int:
    return hw83q4.one() + three()


print("result", g())
