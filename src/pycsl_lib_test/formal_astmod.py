# Formal tests for pycsl_lib/astmod — ast module
from pycsl_lib.astmod import (parse, dump, literal_eval, unparse,
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


def test_literal_eval_unconstrained(node: int) -> int:
    """literal_eval is honestly unconstrained (no >= 0; see §4.4 / P5c)."""
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


# --- P3: \in_scope on definitely-assigned locals (07-1839) ---

#@ requires node >= 0
#@ ensures \in_scope(node)
#@ ensures \in_scope(r)
def test_in_scope_after_copy_location(node: int) -> int:
    """\in_scope is decided TRUE for params and assigned locals."""
    r: int = copy_location(node, node)
    return r


#@ requires src >= 0
#@ ensures \in_scope(src)
#@ ensures \in_scope(tree)
def test_in_scope_after_parse(src: int) -> int:
    """parse result is definitely assigned → in scope."""
    tree: int = parse(src)
    return tree


# --- P4: isinstance on typed params (07-1839) ---

#@ requires isinstance(x, int)
#@ ensures isinstance(x, object)
#@ assigns \nothing
def test_isinstance_int_param(x: int) -> int:
    """isinstance(x:int, int) and isinstance(x, object) both decided TRUE."""
    return x


#@ requires isinstance(s, str)
#@ assigns \nothing
def test_isinstance_str_param(s: str) -> int:
    """isinstance(s:str, str) decided TRUE."""
    return 0
