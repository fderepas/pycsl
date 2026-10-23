r"""bytes equality"""
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    return b"ab" == b"ba"


if __name__ == "__main__":
    print("CPython:", probe())
