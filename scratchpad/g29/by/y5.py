r"""int.to_bytes big endian first byte"""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    return (258).to_bytes(2, "big")[0]


if __name__ == "__main__":
    print("CPython:", probe())
