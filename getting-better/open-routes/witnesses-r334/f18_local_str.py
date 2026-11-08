
class C:
    def __init__(self) -> None:
        x = "ab"
        self.s = x

#@ assigns \nothing
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.s * 0

if __name__ == "__main__":
    assert g() == 0, g()
