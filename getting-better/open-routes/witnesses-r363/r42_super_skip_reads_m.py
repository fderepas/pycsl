class A:
    def __init__(self) -> None:
        self.x = 1

class M(A):
    def __init__(self) -> None:
        super().__init__()
        self.m = 0

class B(M):
    def __init__(self) -> None:
        super(M, self).__init__()
        self.n = 0

#@ no_exception \all
def f(b: B) -> int:
    return b.m

if __name__ == "__main__":
    print(f(B()))
