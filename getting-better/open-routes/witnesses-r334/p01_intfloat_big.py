
class C:
    def __init__(self) -> None:
        self.r = 3.0

#@ assigns \nothing
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = C()
    return 1 if c.r * 10**17 + 1 != c.r * 10**17 else 0

if __name__ == "__main__":
    assert g() == 1, g()
