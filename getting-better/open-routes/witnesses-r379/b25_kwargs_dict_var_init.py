class C:
    def __init__(self, x: int) -> None:
        self.x = x

#@ no_exception \all
def f() -> int:
    kw = {"y": 1}
    c = C(**kw)
    return 1

if __name__ == "__main__":
    print(f())
