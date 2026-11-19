
class C:
    def __init__(self) -> None:
        x = "ab"
        self.s = x

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.s - c.s

if __name__ == "__main__":
    assert g() == 0, g()
