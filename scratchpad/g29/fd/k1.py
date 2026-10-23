r"""G29 FD1 — a KEYWORD-ONLY function parameter default, omitted at the call."""
_ = 0  # anchor


#@ ensures \result == k
def f(*, k: int = 5) -> int:
    return k


#@ ensures \result == 0
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
