"""v27 AGREE — a NEGATIVE repeat count gives the EMPTY string: `'ab' * -3` is '', so its length is 0 and not the -6 that multiplying the length would give."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    s: str = "ab"
    return len(s * -3)


if __name__ == "__main__":
    print(f())
