"""v04 AGREE — Python's 'or' returns an OPERAND, not a bool: 0 or 5 is 5."""


#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    a: int = 0
    b: int = 5
    return a or b


if __name__ == "__main__":
    print(f())
