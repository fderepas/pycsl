"""PyCSL mock for Python's ast module.

Provides trusted stubs for AST operations.
NodeVisitor and NodeTransformer modelled as classes.
"""
_ = 0  # anchor

# ── NodeVisitorObj class ────────────────────────────────────────────

""  # pycsl
#@ class invariant self._visited >= 0
class NodeVisitorObj:
    def __init__(self):
        self._visited = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._visited == \old(self._visited) + 1
    #@ assigns self._visited
    def visit(self, node: int) -> int:
        self._visited += 1
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.NodeVisitor.generic_visit
#@ requires True
#@ ensures True
#@ assigns self._visited
    def generic_visit(self, node: int) -> int:
        return 0

# ── NodeTransformerObj class ────────────────────────────────────────

#@ class invariant self._transformed >= 0
class NodeTransformerObj:
    def __init__(self):
        self._transformed = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._transformed == \old(self._transformed) + 1
    #@ assigns self._transformed
    def visit(self, node: int) -> int:
        self._transformed += 1
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
    def generic_visit(self, node: int) -> int:
        return 0

# ── Module-level functions ──────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.parse
#@ requires optimize >= -1
#@ ensures True
def parse(source: int, filename: int, mode: int, type_comments: int, feature_version: int, optimize: int, ast_module: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
def unparse(ast_obj: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.literal_eval
# cite:_note: real return type is Any (str|bytes|int|float|complex|tuple|list|dict|set|bool|None);
# cite:_note: the int->int stub cannot express the polymorphic return contract — L3 ceiling.
# cite:_note: input constraint (must be a valid literal expression) is also inexpressible on the int stub.
#@ ensures True
def literal_eval(node_or_string: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.get_docstring
#@ requires clean == 0 or clean == 1
#@ ensures True
def get_docstring(node: int, clean: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.dump
#@ ensures True
def dump(node: int, annotate_fields: int, include_attributes: int, color: int, indent: int, show_empty: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.fix_missing_locations
#@ ensures \result == node
def fix_missing_locations(node: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.increment_lineno
#@ ensures True
def increment_lineno(node: int, n: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.copy_location
#@ ensures \result == new_node
def copy_location(new_node: int, old_node: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.iter_fields
#@ ensures True
def iter_fields(node: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.iter_child_nodes
#@ ensures True
def iter_child_nodes(node: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.walk
#@ ensures True
def walk(node: int) -> int:
    return 0
