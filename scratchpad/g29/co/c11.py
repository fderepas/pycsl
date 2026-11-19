r"""G29 CO-C11 — comprehension/iteration builtin probe (claim != truth; CPython 5)."""
_ = 0  # anchor


#@ ensures \result != 5
def probe() -> int:
    x = 5
    xs = [x for x in range(3)]
    return x


if __name__ == "__main__":
    print("CPython:", probe())
