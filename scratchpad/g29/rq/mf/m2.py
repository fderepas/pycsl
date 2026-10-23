import helper167
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    helper167.fget(0)
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
