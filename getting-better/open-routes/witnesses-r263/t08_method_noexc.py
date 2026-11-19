# FALSE: no_exception \all, but CPython raises RecursionError (unbounded self-recursion).
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ no_exception \all
    def m(self, k: int) -> int:
        return self.m(k)

if __name__ == "__main__":
    print(C().m(1))
