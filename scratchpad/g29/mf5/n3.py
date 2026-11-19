from lib5 import div
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        v = div(0)
    except ZeroDivisionError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
