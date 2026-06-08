# pure_lib/astmod — formal model for ast (Abstract Syntax Trees)
#
# Models the CPython ast utility functions with formal contracts.
# Node types (AST, Module, FunctionDef, etc.) are C-level objects and not
# modelled — we represent AST nodes as opaque int handles (node_id >= 0).
# Functions operating on trees produce bounded results.


#@ requires source >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def parse(source: int) -> int:
    """RST: 'Parse source into an AST node.'
    Returns an AST node handle (non-negative)."""
    return 0


#@ requires node >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def dump(node: int) -> int:
    """RST: 'Return a formatted dump of the tree in node.'
    Returns string length of the dump output."""
    return 1


#@ requires node >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def literal_eval(node: int) -> int:
    """RST: 'Evaluate an expression node or a string containing only a Python literal.'
    Returns the evaluated value as int."""
    return 0


#@ requires node >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def unparse(node: int) -> int:
    """RST: 'Unparse an AST object and generate a string with code.'
    Returns string length of the generated code."""
    return 1


#@ requires node >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def get_docstring(node: int) -> int:
    """RST: 'Return the docstring for the given node.'
    Returns string length (0 if no docstring)."""
    return 0


#@ requires new_node >= 0
#@ requires old_node >= 0
#@ ensures \result == new_node
#@ assigns \nothing
def copy_location(new_node: int, old_node: int) -> int:
    """RST: 'Copy source location from old_node to new_node.'
    Returns new_node with location fields set."""
    return new_node


#@ requires node >= 0
#@ ensures \result == node
#@ assigns \nothing
def fix_missing_locations(node: int) -> int:
    """RST: 'Set missing location information on node and children.'
    Returns the node."""
    return node


#@ requires node >= 0
#@ requires n >= 0
#@ ensures \result == node
#@ assigns \nothing
def increment_lineno(node: int, n: int) -> int:
    """RST: 'Increment the line number of each node by n.'
    Returns the node."""
    return node


#@ requires node >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def iter_fields(node: int) -> int:
    """RST: 'Yield (fieldname, value) pairs for each field in node._fields.'
    Returns count of fields yielded."""
    return 0


#@ requires node >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def iter_child_nodes(node: int) -> int:
    """RST: 'Yield all direct child nodes of node.'
    Returns count of children yielded."""
    return 0


#@ requires node >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def walk(node: int) -> int:
    """RST: 'Recursively yield all descendant nodes in the tree starting at node.'
    Returns count of nodes visited."""
    return 1
