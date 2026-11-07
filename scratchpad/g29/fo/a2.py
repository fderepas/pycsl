r"""return in finally swallows exception"""
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    try:
        raise ValueError()
    except ValueError:
        return 1
    finally:
        return 2


if __name__ == "__main__":
    print("CPython:", probe())
