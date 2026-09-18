r"""except handler variable deleted"""
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    r = 0
    try:
        raise KeyError()
    except KeyError:
        r = 1
    finally:
        r = r + 1
    return r


if __name__ == "__main__":
    print("CPython:", probe())
