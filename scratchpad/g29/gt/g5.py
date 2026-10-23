r"""G29 GT5 — mutual recursion without variant, diverging."""
_ = 0  # anchor


#@ ensures \result == 1
def ping(n: int) -> int:
    return pong(n)


#@ ensures \result == 2
def pong(n: int) -> int:
    return ping(n)


#@ ensures \result == 7
def probe() -> int:
    return ping(0)


if __name__ == "__main__":
    print("CPython:", probe())
