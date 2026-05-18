"""Test 0080 — Python Reference 3.3.3.1: Metaclasses"""
_ = 0  # anchor
#@ ensures \result == 0
def test_metaclasses() -> int:
    """Metaclasses customize class creation."""
    class Meta(type):
        def __new__(mcs, name, bases, ns):
            cls = super().__new__(mcs, name, bases, ns)
            cls._count = 0
            return cls
    class C(metaclass=Meta):
        pass
    assert C._count == 0
    return 0

if __name__ == "__main__":
    assert test_metaclasses() == 0
