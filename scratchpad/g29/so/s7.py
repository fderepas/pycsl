r"""max of strings"""
_ = 0  # anchor


#@ ensures \result == "B"
def probe() -> str:
    return max("a", "B")


if __name__ == "__main__":
    print("CPython:", probe())
