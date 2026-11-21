class A:
    __slots__ = ("__x",)
    def __init__(self) -> None:
        self.__x = 1

#@ no_exception \all
def f(a: A) -> int:
    a.__x = 2
    return 0

if __name__ == "__main__":
    print(f(A()))
