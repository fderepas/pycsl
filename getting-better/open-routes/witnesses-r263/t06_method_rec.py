# FALSE: method self-recursion, no decrease
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    def m(self, k: int) -> int:
        return self.m(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    print(C().m(1))
