"""v65 AGREE — `**` is exponentiation, not xor: `2 ** 10` is 1024."""


#@ ensures \result == 1024
#@ assigns \nothing
def f() -> int:
    return 2 ** 10


if __name__ == "__main__":
    print(f())
