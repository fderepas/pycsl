#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    i = 0
    #@ requires y > 0
    #@ no_exception \all
    def g(y: int = i) -> int:
        return 1 // y - 1 // y
    i = 5
    return g()

if __name__ == "__main__":
    assert f() == 0
