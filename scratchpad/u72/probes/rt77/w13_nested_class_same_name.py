class C:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


#@ ensures \result == 2
def outer() -> int:
    class C:
        def __init__(self) -> None:
            self.v = 0

        #@ ensures \result == 2
        #@ assigns \nothing
        def m(self) -> int:
            return 2
    return 2


#@ ensures \result == 2
def g() -> int:
    o = C()
    return o.m()

if __name__ == "__main__":
    print(g())
