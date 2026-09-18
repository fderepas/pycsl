r"""startswith empty"""
_ = 0  # anchor


#@ ensures \result == False
def probe() -> bool:
    s = "abc"
    return s.startswith("")


if __name__ == "__main__":
    print("CPython:", probe())
