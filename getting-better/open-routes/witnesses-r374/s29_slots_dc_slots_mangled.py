class A:
    __slots__ = ("__v",)

class B(A):
    __slots__ = ("w",)
    def __init__(self) -> None:
        self.w = 1
        self.__v = 2

#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    b = B()
    return b.w

if __name__ == "__main__":
    print(f())
