# Formal tests for pure_lib/plat — platform module
from pure_lib.plat import system, machine, python_version, architecture


def test_system_str() -> str:
    """system returns a string."""
    return system()


def test_machine_str() -> str:
    """machine returns a string."""
    return machine()


#@ ensures \result >= 0
def test_architecture_nonneg() -> int:
    """architecture returns non-negative."""
    return architecture()
