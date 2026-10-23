import helper176
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        helper176.fgo(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
