"""v29 AGREE — a slice upper bound past the end is CLAMPED, not an error and not honoured: `'abcde'[1:100]` is 'bcde', length 4."""


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    s: str = "abcde"
    return len(s[1:100])


if __name__ == "__main__":
    print(f())
