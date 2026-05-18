"""Test 0082 — Python Reference 3.3.3.3: Determining the appropriate metaclass"""
_ = 0  # anchor
#@ ensures \result == 0
def test_determining_metaclass() -> int:
    """The most derived metaclass is used."""
    class Meta(type): pass
    class C(metaclass=Meta): pass
    assert type(C) is Meta
    return 0

if __name__ == "__main__":
    assert test_determining_metaclass() == 0
