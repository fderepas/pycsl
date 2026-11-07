r"""raise in a nested if inside a loop"""
_ = 0  # anchor


class MyErr(ValueError):
    pass


#@ ensures \result == 0
def probe() -> int:
    try:
        for i in range(3):
            if i == 1:
                raise MyErr()
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
