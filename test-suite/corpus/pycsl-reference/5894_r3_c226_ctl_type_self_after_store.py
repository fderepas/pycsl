r"""Test 5894 -- driver run #3 route #226 polarity flip CONTROL (expected PASS): `self.x = k` under `#@ requires k >= 0`, then `self.tag = type(self).__name__` (the 4574 shape: `type(self)` is not an escape); goal `forall x k : int. x = k -> (k >= 0) -> ..`.
"""
# pycsl-expected: PASS


#@ class invariant self.x >= 0
class B:
    #@ requires k >= 0
    def __init__(self, k: int) -> None:
        self.x = k
        self.tag = type(self).__name__

    #@ ensures \result >= 0
    #@ assigns \nothing
    def get(self) -> int:
        return self.x


if __name__ == "__main__":
    print(B(4).get())
