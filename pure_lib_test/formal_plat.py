# Formal tests for pure_lib/plat — platform module
from pure_lib.plat import system, machine, python_version, architecture


#@ ensures \result >= 0
def test_system_nonneg() -> int:
    """system returns non-negative."""
    return system()


#@ ensures \result >= 0
def test_machine_nonneg() -> int:
    """machine returns non-negative."""
    return machine()


#@ ensures \result >= 0
def test_python_version_nonneg() -> int:
    """python_version returns non-negative."""
    return python_version()


#@ ensures \result >= 0
def test_architecture_nonneg() -> int:
    """architecture returns non-negative."""
    return architecture()
