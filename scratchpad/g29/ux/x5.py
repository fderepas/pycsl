r"""raise from inside handler replaced exception type"""
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    try:
        try:
            raise ValueError()
        except ValueError:
            raise KeyError()
    except KeyError:
        return 9
    except ValueError:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
