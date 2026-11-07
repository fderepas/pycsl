r"""module-qualified raise via class attribute alias"""
_ = 0  # anchor


class MyErr(ValueError):
    pass


Alias = MyErr


#@ ensures \result == 0
def probe() -> int:
    try:
        raise Alias()
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
