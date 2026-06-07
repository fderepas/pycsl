# Formal tests for pure_lib/astmod — ast module
from pure_lib.astmod import parse, dump


#@ requires source >= 0
#@ ensures \result >= 0
def test_parse_nonneg(source: int) -> int:
    """parse returns non-negative node count."""
    return parse(source)


#@ requires node >= 0
#@ ensures \result >= 0
def test_dump_nonneg(node: int) -> int:
    """dump returns non-negative string length."""
    return dump(node)
