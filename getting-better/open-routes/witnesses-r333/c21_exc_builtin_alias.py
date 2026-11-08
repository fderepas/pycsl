class _ValueError(Exception):
    pass

#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def g(n: int) -> int:
    try:
        raise _ValueError()
    except ValueError:
        return 1
    return 0

if __name__ == "__main__":
    assert g(0) == 1, g(0)
