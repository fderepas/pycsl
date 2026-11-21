r"""G29 GT3 — while True with a return that is never reached... actually reached at i==3."""
_ = 0  # anchor


#@ ensures \result == 4
def probe() -> int:
    i = 0
    while True:
        if i == 3:
            return i
        i += 1


if __name__ == "__main__":
    print("CPython:", probe())
