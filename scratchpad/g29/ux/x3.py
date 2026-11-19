r"""handler order: first matching wins"""
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    try:
        raise KeyError()
    except LookupError:
        return 1
    except KeyError:
        return 2


if __name__ == "__main__":
    print("CPython:", probe())
