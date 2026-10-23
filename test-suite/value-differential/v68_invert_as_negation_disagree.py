"""v68 DISAGREE — the plain-negation reading of `~`. Python's `~5 + 10` is 4; this claims the 5 that `-5 + 10` would give."""


#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    x: int = 5
    return ~x + 10


if __name__ == "__main__":
    print(f())
