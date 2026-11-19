class E(ValueError):
    pass

#@ no_exception \all
#@ ensures \result == 9 or \result == 0
def g(x: int) -> int:
    try:
        if x < 0:
            raise E()
    except ValueError:
        return 9
    return 0

if __name__ == "__main__":
    assert g(-1) == 9
