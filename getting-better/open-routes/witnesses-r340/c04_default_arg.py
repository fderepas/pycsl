#@ ensures \result == 2
def f() -> int:
    x = 1
    def g(y: int = x) -> int:
        return y
    x = 2
    return g()

if __name__ == "__main__":
    assert f() == 2
