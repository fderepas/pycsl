r"""str.find missing"""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    return "abc".find("z") + 1


if __name__ == "__main__":
    print("CPython:", probe())
