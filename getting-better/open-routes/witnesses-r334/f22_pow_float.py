
class C:
    def __init__(self) -> None:
        self.r = 10 ** -1

#@ assigns \nothing
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return 1 if c.r * 10 == 1 else 0

if __name__ == "__main__":
    assert g() == 0, g()
