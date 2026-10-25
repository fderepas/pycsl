r"""Test 5172 -- gen #37 route #380 (expected PASS): CONTROL: `super().__init__(k + 100)` matching `A.__init__(self, k)` passes the new `super().__init__` arity check: `B(7).get() == 107` (CPython ok).
"""
# pycsl-expected: PASS
class A:
    def __init__(self, k: int) -> None:
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self, k: int) -> None:
        super().__init__(k + 100)
        self.y = 1


#@ ensures \result == 107
#@ assigns \nothing
def probe() -> int:
    b = B(7)
    return b.get()

if __name__ == "__main__":
    print(probe())
