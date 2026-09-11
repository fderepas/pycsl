"""v16 AGREE — in Python a bool IS an int, so True + True is 2, not a collapsed 1."""


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    a: bool = True
    b: bool = True
    return a + b


if __name__ == "__main__":
    print(f())
