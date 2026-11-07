from lib5 import div
_ = 0  # anchor


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    v = div(0)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
