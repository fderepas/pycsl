r"""G29 FD3 — a function default that is a MODULE CONSTANT, omitted."""
_ = 0  # anchor
K = 5


#@ ensures \result == k
def f(k: int = K) -> int:
    return k


#@ ensures \result == 0
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
