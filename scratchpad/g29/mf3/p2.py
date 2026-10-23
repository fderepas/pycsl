from helper178 import C
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        v = c.get()
    except KeyError:
        return 9
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
