r"""bytearray store and read"""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    b = bytearray(2)
    b[1] = 7
    return b[1]


if __name__ == "__main__":
    print("CPython:", probe())
