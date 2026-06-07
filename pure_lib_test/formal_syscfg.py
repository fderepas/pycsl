# Formal tests for pure_lib/syscfg — sysconfig module
from pure_lib.syscfg import get_config_var, get_config_vars


#@ requires name >= 0
#@ ensures \result >= 0
def test_get_var_nonneg(name: int) -> int:
    """get_config_var returns non-negative."""
    return get_config_var(name)


#@ ensures \result >= 0
def test_get_vars_nonneg() -> int:
    """get_config_vars returns non-negative."""
    return get_config_vars()
