r"""G29 RQ9 — a violated `requires` on a module function (control)."""
_ = 0  # anchor


#@ requires d != 0
#@ ensures \result == 1
def get(d: int) -> int:
    return d // d


#@ ensures \result == 5
def probe() -> int:
    get(0)
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
