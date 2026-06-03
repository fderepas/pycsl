"""visitor_base — a verifiable NodeVisitor-shaped base imported by 0448 to
exercise cross-module inheritance of a base's *methods* behind a *module*
import (Layer A′ + B + C).

`NodeVisitor` carries a concrete `_depth` field (a field-less class is modeled
as `int`, not a record, and so cannot be a base in the IR monomorphizer), a
class invariant, and two body-verified methods. A subclass that extends it via
`import ... ; class X(mod.NodeVisitor)` inherits `visit`/`generic_visit`, and a
driver calling the inherited `visit` gets its postcondition at the call site.
This is the miniature of `src/pycsl_lib/ast.py`'s `NodeVisitor`.
"""


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
