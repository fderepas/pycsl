r"""G29 CO-C4 — comprehension/iteration builtin probe (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    xs = [1, 2, 3]
    ys = [10, 20]
    return len(list(zip(xs, ys)))


if __name__ == "__main__":
    print("CPython:", probe())
