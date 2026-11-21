
class C:
    def __init__(self) -> None:
        self.r, self.s = 2.5, 1

#@ assigns \nothing
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = C()
    return 1 if c.r % 1 == 0 else 0

if __name__ == "__main__":
    assert g() == 1, g()
