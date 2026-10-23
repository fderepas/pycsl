class Base(Exception):
    pass

class KeyError(Base):
    pass

#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise KeyError("x")
    except Base:
        return 99
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
