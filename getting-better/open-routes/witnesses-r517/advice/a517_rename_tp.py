# advice of PYCSL-R517-TYPE-PARAM-NAME-READ applied to g823_a9001 (`def f[K](n)` reading K): rename the type parameter
K = 5


#@ no_exception \all
#@ ensures \result == n // 5
def f[T](n: int) -> int:
    return n // K


if __name__ == "__main__":
    print("result", f(10))
