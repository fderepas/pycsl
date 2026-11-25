r"""Test 10497 -- run #9 u75, review rt83 o4 (u73 INTRODUCED over-refusal, PASS). A CLASS imported from a
local module (`from zu75h.k import Base`) used as a class base beside an unrelated `self.b = 1`: a class
base that is a class never reaches `__mro_entries__` (PEP 560 calls it only for non-type bases), so it is no
module escape; `cd <tree root> && python <this file>` prints "result 4" and pycsl proves it.
"""
# pycsl-expected: PASS
from zu75h.k import three, Base


class D(Base):
    pass


class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g() -> int:
    c = C()
    return c.b + three()


if __name__ == "__main__":
    print("result", g())
