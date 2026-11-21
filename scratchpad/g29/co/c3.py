r"""G29 CO-C3 — comprehension/iteration builtin probe (claim != truth; CPython 10)."""
_ = 0  # anchor


#@ ensures \result != 10
def probe() -> int:
    return sum(x for x in range(5))


if __name__ == "__main__":
    print("CPython:", probe())
