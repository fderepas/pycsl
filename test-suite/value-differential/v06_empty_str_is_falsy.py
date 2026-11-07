"""v06 AGREE — the empty string is FALSY, so the branch is not taken."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    s: str = ""
    if s:
        return 1
    return 0


if __name__ == "__main__":
    print(f())
