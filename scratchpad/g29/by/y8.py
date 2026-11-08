r"""bytearray append len"""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    b = bytearray()
    b.append(1)
    return len(b)


if __name__ == "__main__":
    print("CPython:", probe())
