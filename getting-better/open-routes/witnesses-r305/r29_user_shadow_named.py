class KeyError(Exception):
    pass

#@ no_exception KeyError
#@ ensures \result == 7
def g(x: int) -> int:
    r = 0
    try:
        if x < 0:
            raise KeyError("x")
        r = 7
    except LookupError:
        r = 7
    return r

if __name__ == "__main__":
    assert g(-1) == 7
