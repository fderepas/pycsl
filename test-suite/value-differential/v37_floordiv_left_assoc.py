"""v37 AGREE — `//` is LEFT-associative: `7 // 2 // 2` is `(7 // 2) // 2` = 3 // 2 = 1, not the 7 that the right-associative `7 // (2 // 2)` would give."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 7 // 2 // 2


if __name__ == "__main__":
    print(f())
