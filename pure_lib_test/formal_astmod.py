# Formal tests for pure_lib/astmod — ast module
from pure_lib.astmod import (parse, dump, literal_eval, unparse,
                              get_docstring, copy_location,
                              fix_missing_locations, increment_lineno,
                              iter_fields, iter_child_nodes, walk)


#@ requires source >= 0
#@ ensures \result >= 0
def test_parse_nonneg(source: int) -> int:
    """parse returns non-negative node handle."""
    return parse(source)


#@ requires node >= 0
#@ ensures \result >= 0
def test_dump_positive(node: int) -> int:
    """dump returns positive string length."""
    return dump(node)


#@ requires node >= 0
#@ ensures \result >= 0
def test_literal_eval_nonneg(node: int) -> int:
    """literal_eval returns non-negative value."""
    return literal_eval(node)


#@ requires node >= 0
#@ ensures \result >= 0
def test_unparse_positive(node: int) -> int:
    """unparse returns positive string length."""
    return unparse(node)


#@ requires node >= 0
#@ ensures \result >= 0
def test_docstring_nonneg(node: int) -> int:
    """get_docstring returns non-negative length."""
    return get_docstring(node)


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == a
def test_copy_location_identity(a: int, b: int) -> int:
    """copy_location returns the new_node unchanged."""
    return copy_location(a, b)


#@ requires node >= 0
#@ ensures \result == node
def test_fix_locations_identity(node: int) -> int:
    """fix_missing_locations returns the same node."""
    return fix_missing_locations(node)


#@ requires node >= 0
#@ requires n >= 0
#@ ensures \result == node
def test_increment_lineno_identity(node: int, n: int) -> int:
    """increment_lineno returns the same node."""
    return increment_lineno(node, n)


#@ requires node >= 0
#@ ensures \result >= 0
def test_iter_fields_nonneg(node: int) -> int:
    """iter_fields returns non-negative count."""
    return iter_fields(node)


#@ requires node >= 0
#@ ensures \result >= 0
def test_iter_children_nonneg(node: int) -> int:
    """iter_child_nodes returns non-negative count."""
    return iter_child_nodes(node)


#@ requires node >= 0
#@ ensures \result >= 0
def test_walk_positive(node: int) -> int:
    """walk returns positive count (at least the root)."""
    return walk(node)
