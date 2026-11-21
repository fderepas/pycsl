class D(Exception):
    def __init__(self, x: int) -> None:
        super().__init__(msg=x)
#@ no_exception \all
def f() -> int:
    e = D(1)
    return 1
if __name__ == "__main__":
    print("result", f())
