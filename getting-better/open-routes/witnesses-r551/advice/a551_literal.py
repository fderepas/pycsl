class C:
    def __init__(self, s: str) -> None:
        self.n = len(s)


#@ no_exception \all
def f(k: int) -> int:
    c = C("ab")
    return 1


if __name__ == "__main__":
    print(f(1))
