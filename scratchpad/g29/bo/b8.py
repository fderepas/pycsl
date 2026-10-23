r"""divmod negative"""
_ = 0  # anchor


#@ ensures \result == -2
def probe() -> int:
    q, r = divmod(-7, 2)
    return q + r


if __name__ == "__main__":
    print("CPython:", probe())
