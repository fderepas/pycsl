# Formal tests for pycsl_lib/logg — logging module
from pycsl_lib.logg import getLogger, basicConfig


#@ requires level >= 0
#@ ensures \result >= 0
def test_getLogger_nonneg(level: int) -> int:
    """getLogger returns non-negative."""
    return getLogger(level)


#@ requires level >= 0
#@ ensures \result >= 0
def test_basicConfig_nonneg(level: int) -> int:
    """basicConfig returns non-negative."""
    return basicConfig(level)
