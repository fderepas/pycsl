class C:
    def __init__(self) -> None:
        self.s = "ab"

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.s - c.s

if __name__ == "__main__":
    assert g() == 0, g()
