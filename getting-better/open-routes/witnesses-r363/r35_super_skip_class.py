class A:
    def __init__(self) -> None:
        self.x = 1

class B(A):
    def __init__(self) -> None:
        self.n = 0
        super(A, self).__init__()

#@ no_exception \all
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    print(f(B()))
