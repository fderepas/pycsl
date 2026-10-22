class E(KeyError):
    pass

#@ no_exception KeyError
#@ ensures \result == 0
def g(x: int) -> int:
    if x < 0:
        raise E()
    return 0

if __name__ == "__main__":
    assert g(-1) == 0
