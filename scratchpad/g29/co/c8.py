r"""G29 CO-C8 — comprehension/iteration builtin probe (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    return 1 if all(x > 0 for x in []) else 0


if __name__ == "__main__":
    print("CPython:", probe())
