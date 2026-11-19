class A(ValueError):
    pass

class B(A):
    pass

#@ no_exception ValueError
#@ ensures \result == 0
def g(x: int) -> int:
    if x < 0:
        raise B()
    return 0

if __name__ == "__main__":
    assert g(-1) == 0
