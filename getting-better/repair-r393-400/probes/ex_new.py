class D(Exception):
    def __new__(cls, a: int) -> "D":
        return super().__new__(cls)
#@ no_exception \all
def f() -> int:
    e = D()
    return 1
if __name__ == "__main__":
    print("result", f())
