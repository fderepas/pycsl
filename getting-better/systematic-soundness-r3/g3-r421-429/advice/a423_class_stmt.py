class B:
    def __init__(self) -> None:
        self.x: int = 1


class D(B):
    pass


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    print(f(D()))
