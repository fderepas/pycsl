r"""bare re-raise caught by outer"""
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    try:
        try:
            raise ValueError()
        except ValueError:
            raise
    except ValueError:
        return 9
    return 1


if __name__ == "__main__":
    print("CPython:", probe())
