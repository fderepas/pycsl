r"""G29 CO-C5 — comprehension/iteration builtin probe (claim != truth; CPython 7)."""
_ = 0  # anchor


#@ ensures \result != 7
def probe() -> int:
    t = 0
    for i, v in enumerate([5, 6], 3):
        t = t + i
    return t


if __name__ == "__main__":
    print("CPython:", probe())
