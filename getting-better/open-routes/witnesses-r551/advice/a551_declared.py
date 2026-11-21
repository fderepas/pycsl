class C:
    def __init__(self, s: str) -> None:
        self.n = len(s)


#@ no_exception \all
def f(k: int, s: str) -> int:
    c = C(s)
    return 1


if __name__ == "__main__":
    print(f(1, "ab"))
