r"""bytes slice len"""
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    return len(b"abcd"[1:3])


if __name__ == "__main__":
    print("CPython:", probe())
