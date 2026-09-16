r"""G29 CO-C1 — comprehension/iteration builtin probe (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    xs = [x * 2 for x in range(4) if x % 2 == 1]
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
