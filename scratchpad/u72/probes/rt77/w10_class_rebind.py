class C:
    def __init__(self) -> None:
        self.v = 0

    def m(self) -> int:
        return 1


class C:
    def __init__(self) -> None:
        self.v = 0

    def m(self) -> int:
        return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    o = C()
    return o.m()

if __name__ == "__main__":
    print(g())
