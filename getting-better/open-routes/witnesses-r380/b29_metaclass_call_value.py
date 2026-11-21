class M(type):
    def __call__(cls, *args: int) -> int:
        return 42

class C(metaclass=M):
    def __init__(self, x: int) -> None:
        self.x = x

#@ ensures \result == 1
def f() -> int:
    c = C(1)
    return c.x

if __name__ == "__main__":
    print(f())
