r"""return in finally overrides try return"""
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    try:
        return 1
    finally:
        return 2


if __name__ == "__main__":
    print("CPython:", probe())
