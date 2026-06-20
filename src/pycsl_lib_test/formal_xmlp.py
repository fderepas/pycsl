# Formal tests for pycsl_lib/xmlp — xml.etree module
from pycsl_lib.xmlp import parse, fromstring


#@ requires length >= 0
#@ ensures \result >= 0
def test_parse_nonneg(length: int) -> int:
    """parse returns non-negative."""
    return parse(length)


#@ requires length >= 0
#@ ensures \result >= 0
def test_fromstring_nonneg(length: int) -> int:
    """fromstring returns non-negative."""
    return fromstring(length)
