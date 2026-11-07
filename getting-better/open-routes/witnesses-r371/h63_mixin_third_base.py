class M:
    def __eq__(self, o: object) -> bool:
        return True

class N:
    pass

class O:
    pass

class D(N, O, M):
    def __init__(self) -> None:
        self.x = 1

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
