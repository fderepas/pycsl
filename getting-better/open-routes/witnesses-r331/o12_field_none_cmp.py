from typing import Optional
class C:
    def __init__(self) -> None:
        self.r: Optional[int] = None

#@ no_exception \all
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.r + 1 > c.r

if __name__ == "__main__":
    assert g() == True, g()
