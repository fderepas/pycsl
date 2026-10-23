r"""Test 1716 — ROUTE #209: the `protects` form's trust boundary asked a PYTHON-AST matcher
about a CSL node, so it had never fired.

`happy own: protects <path> except <fn>` injects `#@ check False` at every direct write to
a protected path outside the exempt set (corpus 0612 is that negative, and it has always
failed correctly). A `\trusted` / `\abstract` function has NO BODY SITE to inject into, so
R1.1 adds a trust boundary: such a function, if not exempt, must carry `#@ \preserves`
when its `#@ assigns` names a protected path.

THE BOUNDARY WAS INERT. It computed the written paths with `_target_dotted_path`, whose
first line is `isinstance(target, ast.Subscript)` — a `pure_ast` matcher. An `#@ assigns`
target is a CSL object: `assigns g.v` parses to `FieldAccess(object='g', field='v')` and
`assigns self.disk[i]` to `FieldSubscript(field='disk', index=Var(name='i'))`. Neither is a
`pure_ast` node, so the matcher returned None for every target, the computed set was
`{None}`, and the intersection with the protected paths was ALWAYS EMPTY.

MEASURED: this file printed "Verification SUCCESS! All contracts formally proven" — a
confinement policy proved of a program in which a non-exempt function writes the protected
field. CPython agrees with the violation: calling `sneaky_stub(5)` sets `g.v` to 5.

Why nothing noticed: the REGION form's identical boundary (0461 positive / 0462 teeth) does
fire, because it reads the declared REGION rather than the assigns targets. No witness
exercised the `protects` form's trust boundary, so an inert check looked like a satisfied
one. Controls: 0611 PROVES, 0612 and 0613 stay refused, 0461 PROVES, 0462 stays refused.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor

#@ happy own:
#@     protects g.v
#@     except setter

#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0


g = C()


#@ requires n >= 0
#@ assigns g.v
def setter(n: int) -> None:
    g.v = n


#@ requires n >= 0
#@ assigns g.v
#@ \trusted
def sneaky_stub(n: int) -> None:
    g.v = n
