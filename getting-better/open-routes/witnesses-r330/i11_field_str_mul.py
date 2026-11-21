class C:
    def __init__(self) -> None:
        self.s = "ab"

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.s * 0 == 0

if __name__ == "__main__":
    assert g() == True, g()
