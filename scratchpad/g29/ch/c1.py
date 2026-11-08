r"""G29 CH1 — a CHAINED assignment `a = b = 5`: are the second and later targets modelled?"""
_ = 0  # anchor


#@ ensures \result == 1
def f() -> int:
    b = 1
    a = b = 5
    return b


if __name__ == "__main__":
    print("CPython:", f())
