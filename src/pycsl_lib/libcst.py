"""PyCSL mock for libcst.

Provides trusted stubs for the LibCST concrete syntax tree library.
CSTVisitor and CSTTransformer modelled as classes.
"""
_ = 0  # anchor

# ── CSTVisitorObj class ─────────────────────────────────────────────

""  # pycsl
#@ class invariant self._visited >= 0
class CSTVisitorObj:
    def __init__(self):
        self._visited = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._visited == \old(self._visited) + 1
    #@ assigns self._visited
    def on_visit(self, node: int) -> int:
        self._visited += 1
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def on_leave(self, node: int) -> int:
        return 0

# ── CSTTransformerObj class ─────────────────────────────────────────

#@ class invariant self._transformed >= 0
class CSTTransformerObj:
    def __init__(self):
        self._transformed = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._transformed == \old(self._transformed) + 1
    #@ assigns self._transformed
    def on_visit(self, node: int) -> int:
        self._transformed += 1
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def on_leave(self, node: int) -> int:
        return 0

# ── Standalone functions ────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def parse_module(code: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def parse_expression(code: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def parse_statement(code: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def MetadataWrapper(cst_module: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def metadata_resolve(wrapper: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def matchers_matches(node: int, matcher_pat: int) -> int:
    return 0
