r"""G29 CO-C2 — comprehension/iteration builtin probe (claim != truth; CPython 6)."""
_ = 0  # anchor


#@ ensures \result != 6
def probe() -> int:
    xs = [x * 2 for x in range(4) if x % 2 == 1]
    return xs[1]


if __name__ == "__main__":
    print("CPython:", probe())
