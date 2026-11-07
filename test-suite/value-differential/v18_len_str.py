"""v18 AGREE — len of a 3-character string is 3."""


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    s: str = "abc"
    return len(s)


if __name__ == "__main__":
    print(f())
