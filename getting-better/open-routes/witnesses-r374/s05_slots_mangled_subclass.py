class A:
    __slots__ = ("__x",)

class B(A):
    __slots__ = ()
    def __init__(self) -> None:
        self.__x = 1

#@ no_exception \all
def f() -> int:
    b = B()
    return 0

if __name__ == "__main__":
    print(f())
