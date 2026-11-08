r"""user exception caught by LookupError-free Exception in non-claiming helper, result used"""
_ = 0  # anchor


class MyErr(ValueError):
    pass


def helper() -> int:
    try:
        raise MyErr()
    except ValueError:
        return 9
    return 0


#@ ensures \result == 0
def probe() -> int:
    return helper()


if __name__ == "__main__":
    print("CPython:", probe())
