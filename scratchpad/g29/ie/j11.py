r"""G29 IE-J11 — a ZeroDivisionError in a helper, caught by the caller."""
_ = 0  # anchor


def get(z: int) -> int:
    return 10 // z


#@ ensures \result == 0
def probe() -> int:
    try:
        v = get(0)
    except ZeroDivisionError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
