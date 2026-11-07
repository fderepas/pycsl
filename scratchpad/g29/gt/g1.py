r"""G29 GT1 — a module global rebound by a function via `global`."""
_ = 0  # anchor
counter = 0


def bump() -> None:
    global counter
    counter = counter + 1


#@ ensures \result == 0
def probe() -> int:
    bump()
    return counter


if __name__ == "__main__":
    print("CPython:", probe())
