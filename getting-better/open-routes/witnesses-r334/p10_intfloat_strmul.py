
class C:
    def __init__(self) -> None:
        self.r = 2.0

#@ no_exception \all
#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    c = C()
    return len("ab" * c.r)

if __name__ == "__main__":
    assert g() == 4, g()
