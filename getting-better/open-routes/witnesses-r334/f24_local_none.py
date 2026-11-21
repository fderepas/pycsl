
class C:
    def __init__(self) -> None:
        x = None
        self.r = x

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.r * 0

if __name__ == "__main__":
    assert g() == 0, g()
