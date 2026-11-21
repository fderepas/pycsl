r"""substring in"""
_ = 0  # anchor


#@ ensures \result == False
def probe() -> bool:
    return "" in "abc"


if __name__ == "__main__":
    print("CPython:", probe())
