class E(Exception):
    pass

class _E(Exception):
    pass

#@ ensures \result == 1
#@ assigns \nothing
def g(n: int) -> int:
    try:
        raise _E()
    except E:
        return 1
    except _E:
        return 2
    return 0

if __name__ == "__main__":
    assert g(0) == 1, g(0)
