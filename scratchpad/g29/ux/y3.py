r"""G29 UX-Y3 — a module function raising ValueError (unannotated), caught by the caller."""
_ = 0  # anchor


def go(v: int) -> int:
    if v < 0:
        raise ValueError()
    return v


#@ ensures \result == 0
def probe() -> int:
    try:
        go(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
