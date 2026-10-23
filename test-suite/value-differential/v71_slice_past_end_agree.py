"""v71 AGREE — a slice whose START is past the end is EMPTY, not an error: `'abc'[5:7]` is '', length 0."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    s: str = "abc"
    return len(s[5:7])


if __name__ == "__main__":
    print(f())
