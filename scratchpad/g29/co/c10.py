r"""G29 CO-C10 — comprehension/iteration builtin probe (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    s = {x % 3 for x in range(10)}
    return len(s)


if __name__ == "__main__":
    print("CPython:", probe())
