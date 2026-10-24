
class C:
    def __init__(self) -> None:
        self.d = {"a": 0.5}

#@ assigns \nothing
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = C()
    return 1 if c.d["a"] % 1 == 0 else 0

if __name__ == "__main__":
    assert g() == 1, g()
