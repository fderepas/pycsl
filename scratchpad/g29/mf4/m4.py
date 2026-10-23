from lib179 import boom
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        boom()
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
