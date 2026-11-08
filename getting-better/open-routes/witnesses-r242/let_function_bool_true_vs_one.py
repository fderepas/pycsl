#@ assigns \nothing
def h(x: int) -> int:
    if isinstance(x, bool):
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    if h(True) == h(1):
        return 1
    return 0


if __name__ == "__main__":
    print(m())
