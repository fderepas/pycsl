#@ no_exception \all
#@ ensures \result == 0
def g(x: int) -> int:
    try:
        if x < 0:
            raise ValueError("neg")
    except ValueError:
        raise KeyError("k")
    return 0

if __name__ == "__main__":
    assert g(-1) == 0
