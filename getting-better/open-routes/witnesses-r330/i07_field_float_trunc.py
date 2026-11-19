class C:
    def __init__(self) -> None:
        self.r = 2.5

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return int(c.r) == c.r

if __name__ == "__main__":
    assert g() == True, g()
