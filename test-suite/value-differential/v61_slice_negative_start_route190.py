"""v61 DISAGREE — a NEGATIVE slice start counts from the END in Python (`'abcde'[-2:]` is 'de', length 2) while Why3's `String.substring` treats `start < 0` as out of bounds and answers the empty string. This claims that 0."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    s: str = "abcde"
    return len(s[0 - 2:])


if __name__ == "__main__":
    print(f())
