"""PyCSL mock for Python's ast module — 0 `\trusted`.

Every stub is either body-verified (its `return` provably satisfies its
contract) or — for the irreducibly-opaque parser entry points (`parse`,
`literal_eval`) — an `#@ \abstract` val defined solely by its contract (a
bodyless, uninterpreted op; NOT a trusted, present-but-unchecked body).
NodeVisitor / NodeTransformer are modelled as classes.
"""
_ = 0  # anchor

# ── NodeVisitor base (body-verified) ────────────────────────────────
# Body-verified base so subclasses inherit visit / generic_visit. Carries a
# concrete `_depth` field (a class with no fields is modeled as `int`, not a
# record, and so cannot be a base in the IR-level monomorphizer) and a class
# invariant pinning it non-negative. Reflective `getattr(self,'visit_'+name)`
# dispatch is not modeled — the base returns a non-negative visit result;
# subclasses override `visit_<Node>` statically.
#@ class invariant self._depth >= 0
class NodeVisitor:
    def __init__(self):
        self._depth = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def generic_visit(self, node: int) -> int:
        return 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def visit(self, node: int) -> int:
        return self.generic_visit(node)

# ── NodeVisitorObj class (stateful counter, body-verified) ──────────

""  # pycsl
#@ class invariant self._visited >= 0
class NodeVisitorObj:
    def __init__(self):
        self._visited = 0

    # cite: https://docs.python.org/3/library/ast.html#ast.NodeVisitor.visit
    #@ requires self._visited >= 0
    #@ ensures self._visited == \old(self._visited) + 1
    #@ assigns self._visited
    def visit(self, node: int) -> int:
        self._visited += 1
        return 0

    # cite: https://docs.python.org/3/library/ast.html#ast.NodeVisitor.generic_visit
    #@ ensures \result == 0
    #@ assigns \nothing
    def generic_visit(self, node: int) -> int:
        return 0

# ── NodeTransformerObj class (stateful counter, body-verified) ──────

#@ class invariant self._transformed >= 0
class NodeTransformerObj:
    def __init__(self):
        self._transformed = 0

    # cite: https://docs.python.org/3/library/ast.html#ast.NodeTransformer.visit
    #@ requires self._transformed >= 0
    #@ ensures self._transformed == \old(self._transformed) + 1
    #@ assigns self._transformed
    def visit(self, node: int) -> int:
        self._transformed += 1
        return 0

    # cite: https://github.com/python/cpython/blob/main/Lib/ast.py
    #@ ensures \result == 0
    #@ assigns \nothing
    def generic_visit(self, node: int) -> int:
        return 0

# ── Module-level functions ──────────────────────────────────────────

# cite: https://docs.python.org/3/library/ast.html#ast.parse
# cite:_note: `parse` IS Python's parser — irreducibly opaque, so it is an
#   `\abstract` val (0 \trusted). Its modellable safety property is the bounded
#   raises set: on a syntactically invalid source it raises SyntaxError, and the
#   returned tree is an uninterpreted value. A `try/except SyntaxError` wrapper
#   around it is therefore total (the C3 `check_code` shape).
#@ \abstract
#@ requires optimize >= -1
#@ ensures \result >= 0
#@ raises SyntaxError when True
def parse(source: int, filename: int, mode: int, type_comments: int, feature_version: int, optimize: int, ast_module: int) -> int:
    return 0

# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ ensures True
#@ assigns \nothing
def unparse(ast_obj: int) -> int:
    return 0

# cite: https://docs.python.org/3/library/ast.html#ast.literal_eval
# cite:_note: literal_eval IS Python's literal parser — irreducibly opaque, so it is
#   modeled as an `\abstract` val (0 \trusted, no unchecked body). The SAFETY guarantee
#   is the bounded raises set: on input that is not a valid Python literal it raises
#   ValueError / SyntaxError and NEVER executes arbitrary code (unlike eval). PyCSL does
#   not model the parser, so the parsed VALUE is uninterpreted (int); what IS proven
#   (corpus 0449) is that a `try/except (ValueError, SyntaxError)` wrapper around it is
#   TOTAL — no input can make it propagate an exception or run code.
# cite:_note: real return type is Any (str|bytes|int|float|complex|tuple|list|dict|set|bool|None);
#   the int return cannot express the polymorphic value — the dict read-back demo is deferred.
#@ \abstract
#@ raises ValueError when True
#@ raises SyntaxError when True
def literal_eval(node_or_string: int) -> int:
    return 0

# cite: https://docs.python.org/3/library/ast.html#ast.get_docstring
#@ requires clean == 0 or clean == 1
#@ ensures True
#@ assigns \nothing
def get_docstring(node: int, clean: int) -> int:
    return 0

# cite: https://docs.python.org/3/library/ast.html#ast.dump
#@ ensures True
#@ assigns \nothing
def dump(node: int, annotate_fields: int, include_attributes: int, color: int, indent: int, show_empty: int) -> int:
    return 0

# cite: https://docs.python.org/3/library/ast.html#ast.fix_missing_locations
#@ ensures \result == node
#@ assigns \nothing
def fix_missing_locations(node: int) -> int:
    return node

# cite: https://docs.python.org/3/library/ast.html#ast.increment_lineno
#@ ensures True
#@ assigns \nothing
def increment_lineno(node: int, n: int) -> int:
    return 0

# cite: https://docs.python.org/3/library/ast.html#ast.copy_location
#@ ensures \result == new_node
#@ assigns \nothing
def copy_location(new_node: int, old_node: int) -> int:
    return new_node

# cite: https://docs.python.org/3/library/ast.html#ast.iter_fields
#@ ensures True
#@ assigns \nothing
def iter_fields(node: int) -> int:
    return 0

# cite: https://docs.python.org/3/library/ast.html#ast.iter_child_nodes
#@ ensures True
#@ assigns \nothing
def iter_child_nodes(node: int) -> int:
    return 0

# cite: https://docs.python.org/3/library/ast.html#ast.walk
#@ ensures True
#@ assigns \nothing
def walk(node: int) -> int:
    return 0
