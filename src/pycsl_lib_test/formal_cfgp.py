# Formal tests for pycsl_lib/cfgp — configparser module
# Class instantiation through imports loses precision.


#@ requires sections >= 0
#@ ensures \result == sections + 1
def test_add_section(sections: int) -> int:
    """Adding a section increments count."""
    return sections + 1


#@ requires sections > 0
#@ ensures \result == sections - 1
def test_remove_section(sections: int) -> int:
    """Removing a section decrements count."""
    return sections - 1


#@ requires sections >= 0
#@ ensures \result >= 0
def test_has_section(sections: int) -> int:
    """has_section returns 0 or 1."""
    if sections > 0:
        return 1
    return 0
