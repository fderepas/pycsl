import hw81x1b
import zf81x1b
from dp81x1b import three


#@ ensures \result == 4
def g() -> int:
    return hw81x1b.one() + three()


print("result", g())
