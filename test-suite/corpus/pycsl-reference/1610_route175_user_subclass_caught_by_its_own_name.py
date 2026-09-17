r"""Test 1610 - ROUTE #175 control (gen #29): the user subclass caught by its OWN name is modelled and `\result == 9` proves.
"""
_ = 0  # anchor


class Base(Exception):
    pass


class Sub(Base):
    pass


#@ ensures \result == 9
def probe() -> int:
    try:
        raise Sub()
    except Sub:
        return 9
    return 0
