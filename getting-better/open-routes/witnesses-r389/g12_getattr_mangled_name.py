class R:
    def __init__(self) -> None:
        self.__k: int = 5


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "_R__k", 0)


if __name__ == "__main__":
    v = f(R())
    print("VIOLATION f =", v) if v != 0 else print("no violation")
