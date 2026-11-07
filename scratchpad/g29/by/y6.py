r"""int.from_bytes little"""
_ = 0  # anchor


#@ ensures \result == 258
def probe() -> int:
    return int.from_bytes(b"\x01\x02", "little")


if __name__ == "__main__":
    print("CPython:", probe())
