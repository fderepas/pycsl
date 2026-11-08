r"""numeric string ordering"""
_ = 0  # anchor


#@ ensures \result == False
def probe() -> bool:
    return "10" < "9"


if __name__ == "__main__":
    print("CPython:", probe())
