K: int = 7
class C:
    x: int
    def __init__(self, n: int) -> None:
        self.x = n + K

#@ ensures \result == 0
def f() -> int:
    c = C(1)
    return c.x
if __name__ == "__main__":
    print(f())
