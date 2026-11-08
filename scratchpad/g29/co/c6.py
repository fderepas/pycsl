r"""G29 CO-C6 — comprehension/iteration builtin probe (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    d = {x % 2: x for x in range(4)}
    return d[0]


if __name__ == "__main__":
    print("CPython:", probe())
