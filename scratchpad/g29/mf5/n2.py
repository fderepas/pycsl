from lib5 import K
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    k = K()
    return k.read() * 0


if __name__ == "__main__":
    print("CPython:", probe())
