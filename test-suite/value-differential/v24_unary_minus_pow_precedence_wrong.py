"""v24 DISAGREE — the (-2)**2 reading of `-2 ** 2`. Python gives -4; this claims the 4 that a model which binds unary minus first would produce."""


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return -2 ** 2


if __name__ == "__main__":
    print(f())
