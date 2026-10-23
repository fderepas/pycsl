r"""string ordering case"""
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    return "a" < "B"


if __name__ == "__main__":
    print("CPython:", probe())
