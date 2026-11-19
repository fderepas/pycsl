class E(Exception):
    pass

#@ raises ValueError when x < 0
#@ ensures \result == 0
def h(x: int) -> int:
    m = x
    if m < 0:
        raise ValueError("neg")
    if m == 3:
        raise E()
    return 0

if __name__ == "__main__":
    assert h(3) == 0
