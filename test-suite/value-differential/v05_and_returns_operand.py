"""v05 AGREE — Python's 'and' returns an OPERAND: 5 and 3 is 3."""


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    a: int = 5
    b: int = 3
    return a and b


if __name__ == "__main__":
    print(f())
