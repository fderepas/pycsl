"""v17 AGREE — 2 ** 10 is 1024. Pins the power operator against an XOR reading."""


#@ ensures \result == 1024
#@ assigns \nothing
def f() -> int:
    return 2 ** 10


if __name__ == "__main__":
    print(f())
