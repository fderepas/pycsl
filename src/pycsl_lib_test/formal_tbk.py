# Formal tests for pycsl_lib/tbk — traceback module
from pycsl_lib.tbk import format_exc, format_tb, extract_tb, print_exc


#@ requires depth >= 0
#@ ensures \result >= depth
def test_format_exc_bounded(depth: int) -> int:
    """format_exc output >= depth."""
    return format_exc(depth)


#@ requires depth >= 0
#@ ensures \result >= depth
def test_format_tb_bounded(depth: int) -> int:
    """format_tb output >= depth."""
    return format_tb(depth)


#@ requires limit >= 0
#@ ensures \result >= 0
def test_extract_nonneg(limit: int) -> int:
    """extract_tb returns non-negative."""
    return extract_tb(limit)


#@ requires depth >= 0
#@ ensures \result >= 0
def test_print_exc_nonneg(depth: int) -> int:
    """print_exc returns non-negative."""
    return print_exc(depth)
