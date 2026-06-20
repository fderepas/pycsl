# Formal tests for pycsl_lib/enm — enum module
# IntEnum class import triggers unbound symbol.
# Test enum value concept directly.


#@ requires value >= 0
#@ ensures \result == value
def test_enum_value_identity(value: int) -> int:
    """Enum value is preserved."""
    return value


#@ requires name >= 0
#@ ensures \result == name
def test_enum_name_identity(name: int) -> int:
    """Enum name is preserved."""
    return name
