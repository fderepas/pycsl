r"""string equality with different case"""
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    return "abc".upper() == "abc"


if __name__ == "__main__":
    print("CPython:", probe())
