from lib179 import C
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    c = C(-1)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
