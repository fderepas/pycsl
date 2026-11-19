#@ class invariant self.x >= 0
class B:
    #@ requires k >= 0
    def __init__(self, k: int) -> None:
        self.x = k
        self.tag = type(self).__name__

#@ ensures \result >= 0
def g() -> int:
    b = B(-1)
    return b.x

if __name__ == "__main__":
    assert g() >= 0
