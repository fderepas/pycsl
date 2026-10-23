from helper167 import fget
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    fget(0)
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
