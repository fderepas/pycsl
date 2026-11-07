from helper167 import C
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    c = C(0)
    c.get()
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
