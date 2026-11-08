"""v68 DISAGREE — the plain-negation reading of `~`. Python gives -6; this claims the -5 that unary minus would give."""


#@ ensures \result == 0 - 5
#@ assigns \nothing
def f() -> int:
    x: int = 5
    return ~x


if __name__ == "__main__":
    print(f())
