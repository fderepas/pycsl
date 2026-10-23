class LookupError(Exception):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise KeyError("x")
    except LookupError:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
