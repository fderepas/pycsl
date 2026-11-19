r"""finally mutation after return value computed"""
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    x = 1
    try:
        return x
    finally:
        x = 2


if __name__ == "__main__":
    print("CPython:", probe())
