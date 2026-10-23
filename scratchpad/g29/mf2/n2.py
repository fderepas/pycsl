from helper176 import C
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        c.go(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
