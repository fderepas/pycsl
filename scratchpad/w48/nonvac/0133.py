"""Test 0133 — Python Reference 6.2.2.1: Private name mangling"""
_ = 0  # anchor


class Holder:
    #@ requires True
    #@ ensures self.__v == 3
    #@ assigns self.__v
    def __init__(self) -> None:
        self.__v = 3

    #@ requires True
    #@ ensures \result == self.__v
    #@ assigns \nothing
    def get(self) -> int:
        return self.__v


#@ ensures \result == 0
#@ assigns \nothing
def test_private_name_mangling() -> int:
    """Ref 6.2.2.1: an identifier of the form `__name` inside a class body is MANGLED to
    `_ClassName__name`, so the attribute written by `__init__` and the one read by `get`
    are the SAME attribute — the mangling is applied consistently within the class. That
    consistency is the obligation: an emitter that mangled one occurrence and not the other
    would give the two contracts different fields and `get` could not be discharged.
    Previously the whole body was `return 0`."""
    c = Holder()
    if c.get() == 4:
        return 0
    return 1


if __name__ == "__main__":
    assert test_private_name_mangling() == 0
