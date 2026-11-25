class C:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def h(self) -> int:
        return 1

    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        #@ ensures \result == 2
        #@ assigns \nothing
        def h() -> int:
            return 2
        return h()

    #@ ensures \result == 2
    #@ assigns \nothing
    def k(self) -> int:
        return self.h()

if __name__ == "__main__":
    print(C().k())
