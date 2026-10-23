r"""G29 CO-Z12 — route #158 control: `all` over a NON-empty literal keeps the faithful fold."""
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    return 1 if all(x > 0 for x in [1, 2]) else 0


if __name__ == "__main__":
    print("CPython:", probe())
