"""v62 DISAGREE — a NEGATIVE slice stop: Python's `'abcde'[:-1]` is 'abcd' (4); the `hi - lo` reading makes the length -1, which Why3 answers with the empty string. This claims that 0."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    s: str = "abcde"
    return len(s[:0 - 1])


if __name__ == "__main__":
    print(f())
