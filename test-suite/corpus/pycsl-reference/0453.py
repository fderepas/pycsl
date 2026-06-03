# pycsl-flags: --memory-model hoare
"""0453 — the literal `check_code` analyzer driver (C3), integrating B1+B2+B4+C2.
Body-verified, 0 \trusted; hoare model.

A `FunctionAnalyzer` subclasses an imported `NodeVisitor` base (B1), calls
`super().__init__()` (B4), inspects `node.name.islower()/.startswith()/.endswith()`
(B2 string predicates over an attribute chain), and is driven by `check_code`,
which builds the analyzer inside a `try`, calls the inherited `visit`, and wraps
an `\abstract` parser (`parse`, raises SyntaxError, C2 shape).

WHAT IS PROVEN: `check_code` returns 0 or 1 (from the ternary) and is TOTAL
(`try/except SyntaxError`). The concrete outcome for a specific source string is
NOT proven — it rests on the opaque parser + the reflective `visit_<Node>`
dispatch, which PyCSL does not model (honest per the plan).

FunctionAnalyzer carries NO own class invariant: a subclass invariant stacked on
the base's invariant currently yields an Unknown construction VC in a driver
(known merged-invariant gap); the `\result ∈ {0,1}` bound comes from the ternary.
"""
import multi_file_lib.visitor_base as vb


class FunctionAnalyzer(vb.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.everything_fine = 1

    #@ ensures \result >= 0
    #@ assigns self.everything_fine
    def visit_FunctionDef(self, node: int) -> int:
        if not node.name.islower() and not (node.name.startswith('__') and node.name.endswith('__')):
            self.everything_fine = 0
        return self.generic_visit(node)


#@ \abstract
#@ ensures \result >= 0
#@ raises SyntaxError when True
def parse(source: int) -> int:
    return 0


#@ requires source >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def check_code(source: int) -> int:
    try:
        tree = parse(source)
        analyzer = FunctionAnalyzer()
        r = analyzer.visit(tree)
        return 1 if analyzer.everything_fine == 1 else 0
    except SyntaxError:
        return 0


if __name__ == "__main__":
    print("PASS")
