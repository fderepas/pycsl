from m634b import R, f


#@ requires r.a == 1
#@ ensures \result == 1
def g(r: R) -> int:
    f(r)
    return r.a


if __name__ == "__main__":
    print("CPython g(R(1,0)) =", g(R(1, 0)))
