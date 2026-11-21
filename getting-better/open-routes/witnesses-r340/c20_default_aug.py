#@ ensures \result == x + 1
def f(x: int) -> int:
    def g(y: int = x) -> int:
        return y
    x += 1
    return g()

if __name__ == "__main__":
    assert f(1) == 2
