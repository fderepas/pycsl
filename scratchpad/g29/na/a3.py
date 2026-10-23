r"""G29 NA3 — walrus in a condition binds the value."""
_ = 0  # anchor


#@ ensures \result == 0
def probe(x: int) -> int:
    if (y := x * 2) > 10:
        return y
    return 0


if __name__ == "__main__":
    print("CPython:", probe(6))
