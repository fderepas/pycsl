"""v70 DISAGREE — the ERASED reading of a bytes index. Python gives 97; this claims the 0 an unmodelled read would produce."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    b: bytes = b"abc"
    return b[0]


if __name__ == "__main__":
    print(f())
