r"""G29 CO-C7 — comprehension/iteration builtin probe (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    return 1 if any(x > 2 for x in [1, 2, 3]) else 0


if __name__ == "__main__":
    print("CPython:", probe())
