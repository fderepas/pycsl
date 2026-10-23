r"""len after replace"""
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    return len("aaa".replace("a", "bb"))


if __name__ == "__main__":
    print("CPython:", probe())
