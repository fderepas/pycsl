class Suppress:
    #@ ensures True
    def __init__(self) -> None:
        self.k: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    def __enter__(self) -> int:
        return 0

    #@ ensures \result == True
    #@ assigns \nothing
    def __exit__(self, a: object, b: object, c: object) -> bool:
        return True


#@ ensures \result == 1
def g(x: int) -> int:
    r = 1
    with Suppress():
        raise ValueError("x")
    return r + 1


if __name__ == "__main__":
    print("CPython g(0) =", g(0))
