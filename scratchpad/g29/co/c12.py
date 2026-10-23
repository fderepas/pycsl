r"""G29 CO-C12 — comprehension/iteration builtin probe (claim != truth; CPython 5)."""
_ = 0  # anchor


#@ ensures \result != 5
def probe() -> int:
    return max([3, 1, 4, 1, 5], default=0)


if __name__ == "__main__":
    print("CPython:", probe())
