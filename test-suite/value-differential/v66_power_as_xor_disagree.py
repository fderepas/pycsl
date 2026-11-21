"""v66 DISAGREE — the XOR reading of `**`. Python gives 1024; this claims the 8 that `2 ^ 10` would give."""


#@ ensures \result == 8
#@ assigns \nothing
def f() -> int:
    return 2 ** 10


if __name__ == "__main__":
    print(f())
