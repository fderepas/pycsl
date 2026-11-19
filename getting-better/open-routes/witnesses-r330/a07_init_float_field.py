class C:
    def __init__(self) -> None:
        self.r = 0.5

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.r % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
