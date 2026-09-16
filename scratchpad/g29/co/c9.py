r"""G29 CO-C9 — comprehension/iteration builtin probe (claim != truth; CPython 6)."""
_ = 0  # anchor


#@ ensures \result != 6
def probe() -> int:
    xs = [[i, j] for i in range(2) for j in range(3)]
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
