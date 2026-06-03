# pycsl-flags: --memory-model hoare
"""0448 — cross-module inheritance of a base's METHODS behind a *module* import
(the literal `import ast; class FunctionAnalyzer(ast.NodeVisitor)` shape), with
a driver calling the INHERITED method. Body-verified, 0 \trusted; hoare model.

Two things this regresses, both gaps before B1 of level-up-your-game-agents.md:

  * Layer A′ — a subclass base referenced through a *dotted module import*
    (`vb.NodeVisitor`) is now resolved and its record + `<class>__*` methods are
    injected, so `_apply_inheritance` monomorphizes `visit`/`generic_visit` onto
    `FunctionAnalyzer`. (`from`-import bases already worked: 0443.)

  * the inherited method's `ensures` reaches a *driver* call site — `run` builds
    a `FunctionAnalyzer` and calls the INHERITED `a.visit(n)`; its `\result >= 0`
    previously lowered to a contract-less abstract op (Unknown goal).

`visit_FunctionDef` is the subclass's own override-shaped method; the base's
reflective `visit_<Node>` routing is not modeled (the cited boundary) — the base
`visit` returns a non-negative result and that is what propagates.
"""
import multi_file_lib.visitor_base as vb


#@ class invariant self.count >= 0
class FunctionAnalyzer(vb.NodeVisitor):
    def __init__(self):
        self.count = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def visit_FunctionDef(self, node: int) -> int:
        return 1


#@ ensures \result >= 0
#@ assigns \nothing
def run(n: int) -> int:
    a = FunctionAnalyzer()
    return a.visit(n)


if __name__ == "__main__":
    a = FunctionAnalyzer()
    assert a.visit(0) == 0
    assert a.visit_FunctionDef(0) == 1
    print("PASS")
