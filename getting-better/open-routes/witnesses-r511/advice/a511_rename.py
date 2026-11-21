# route #511 advice followed: witness 8140 with the local class renamed (`class Kc`), a name
# bound nowhere else in the file; `n // K` now reads the module constant in CPython too.
K = 5


#@ requires n >= 0
#@ ensures \result == n // 5
#@ no_exception \all
def f(n: int) -> int:
    class Kc:
        pass
    return n // K


if __name__ == "__main__":
    print(f(10))
