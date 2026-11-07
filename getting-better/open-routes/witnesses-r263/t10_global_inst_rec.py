# FALSE (termination): free function -> method on a fresh instance -> free function.
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 3
    #@ assigns \nothing
    def m(self, k: int) -> int:
        return g(k)

#@ ensures \result == 3
#@ assigns \nothing
def g(k: int) -> int:
    c = C()
    return c.m(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    print(g(1))
