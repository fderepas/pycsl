r"""G29 SC3 — a user function with a body (not pure) called inside a contract."""
_ = 0  # anchor


def inc(x: int) -> int:
    return x + 1


#@ ensures \result == inc(x)
def probe(x: int) -> int:
    return x


if __name__ == "__main__":
    print("CPython:", probe(0), inc(0))
