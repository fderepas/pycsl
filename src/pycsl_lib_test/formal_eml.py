# Formal tests for pycsl_lib/eml — email module
from pycsl_lib.eml import create_message, get_body, as_string


#@ requires body >= 0
#@ ensures \result >= 0
def test_create_nonneg(body: int) -> int:
    """create_message returns non-negative."""
    return create_message(body)


#@ requires msg >= 0
#@ ensures \result >= 0
def test_body_nonneg(msg: int) -> int:
    """get_body returns non-negative."""
    return get_body(msg)


#@ requires msg >= 0
#@ ensures \result >= 0
def test_string_nonneg(msg: int) -> int:
    """as_string returns non-negative."""
    return as_string(msg)
