from m634 import R, f


#@ requires r.b == 0
#@ ensures \result == 0
def g(r: R) -> int:
    f(r)
    return r.b


if __name__ == "__main__":
    print("CPython g(R(1,0)) =", g(R(1, 0)))
