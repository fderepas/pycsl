r"""G29 GT6 — nonlocal rebinding inside a nested function."""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    x = 0

    def inc() -> None:
        nonlocal x
        x += 1

    inc()
    return x


if __name__ == "__main__":
    print("CPython:", probe())
