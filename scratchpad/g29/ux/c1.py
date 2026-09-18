r"""tuple handler containing the base"""
_ = 0  # anchor


class MyErr(ValueError):
    pass


#@ ensures \result == 0
def probe() -> int:
    try:
        raise MyErr()
    except (KeyError, ValueError):
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
