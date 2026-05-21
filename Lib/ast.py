"""PyCSL mock for Python's ast module — Abstract Syntax Tree classes and manipulation."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def parse(source: int, filename: int, mode: int, type_comments: int, feature_version: int, optimize: int, module_: int) -> int:
    """Mock: Parse the source into an AST node.  Equivalent to ``compile(source, filename, mode, flags=FLAGS_VALUE, optimize=optimize..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unparse(ast_obj: int) -> int:
    """Mock: Unparse an :class:`ast.AST` object and generate a string with code that would produce an equivalent :class:`ast.AST` obj..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def literal_eval(node_or_string: int) -> int:
    """Mock: Evaluate an expression node or a string containing only a Python literal or container display.  The string or node provi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_docstring(node: int, clean: int) -> int:
    """Mock: Return the docstring of the given *node* (which must be a :class:`FunctionDef`, :class:`AsyncFunctionDef`, :class:`Class..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_source_segment(source: int, node: int, padded: int) -> int:
    """Mock: Get source code segment of the *source* that generated *node*. If some location information (:attr:`~ast.AST.lineno`, :a..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def fix_missing_locations(node: int) -> int:
    """Mock: When you compile a node tree with :func:`compile`, the compiler expects :attr:`~ast.AST.lineno` and :attr:`~ast.AST.col_..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def increment_lineno(node: int, n: int) -> int:
    """Mock: Increment the line number and end line number of each node in the tree starting at *node* by *n*. This is useful to 'mov..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copy_location(new_node: int, old_node: int) -> int:
    """Mock: Copy source location (:attr:`~ast.AST.lineno`, :attr:`~ast.AST.col_offset`, :attr:`~ast.AST.end_lineno`, and :attr:`~ast..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iter_fields(node: int) -> int:
    """Mock: Yield a tuple of ``(fieldname, value)`` for each field in ``node._fields`` that is present on *node*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iter_child_nodes(node: int) -> int:
    """Mock: Yield all direct child nodes of *node*, that is, all fields that are nodes and all items of fields that are lists of nod..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def walk(node: int) -> int:
    """Mock: Recursively yield all descendant nodes in the tree starting at *node* (including *node* itself), in no specified order. ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dump(node: int, annotate_fields: int, include_attributes: int, color: int, indent: int, show_empty: int) -> int:
    """Mock: Return a formatted dump of the tree in *node*.  This is mainly useful for debugging purposes.  If *annotate_fields* is t..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def compare(a: int, b: int, compare_attributes: int) -> int:
    """Mock: Recursively compares two ASTs. *compare_attributes* affects whether AST attributes are considered in the comparison. If ..."""
    return 0
