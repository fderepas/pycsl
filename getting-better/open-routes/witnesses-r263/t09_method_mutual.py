# FALSE (termination): a <-> b mutual method recursion, no variant, no diverges.
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 5
    #@ assigns \nothing
    def a(self, k: int) -> int:
        return self.b(k)

    #@ ensures \result == 5
    #@ assigns \nothing
    def b(self, k: int) -> int:
        return self.a(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    print(C().a(1))
