r"""bytes concat len"""
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    return len(b"ab" + b"cd")


if __name__ == "__main__":
    print("CPython:", probe())
