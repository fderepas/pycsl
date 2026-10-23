r"""int of 2.9999999999999999 literal"""
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    return int(2.9999999999999999)


if __name__ == "__main__":
    print("CPython:", probe())
