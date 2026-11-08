r"""Test 1718 — ROUTE #210: a `#@ check False` injected into a body that is never lowered
is not a check, and route #209's boundary keyed on the DECLARATION a liar controls.

The `protects` form stamps every non-exempt write site with an unprovable `#@ check` —
that is how corpus 0612 fails. A `\trusted` / `\abstract` body is NOT LOWERED, so its
stamped sites evaporate. Route #209 added the trust boundary for that case, but keyed it
on the stub's DECLARED `#@ assigns`: a stub that declares `assigns \nothing` while its
BODY writes the protected path walks past both mechanisms.

MEASURED: this file printed "Verification SUCCESS! All contracts formally proven" —
confinement proved of a program whose non-exempt `liar` sets `g.v`, with no `#@ \preserves`
anywhere. CPython agrees with the violation.

The body is RIGHT THERE in the AST: `\trusted` means "not lowered", not "not readable",
and `bin/check-trusted-frame-honesty.py` already compares stub frames against live bodies
for exactly this reason. The repair reads the sites the policy ALREADY collects and turns
one inside a trusted function into a refusal instead of an inert stamp.

Controls: 1717 (the same shape WITH `#@ \preserves`) still PASSES, 0611 PROVES,
0612/0613/1716 stay refused.
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
#@ assigns \nothing
#@ \trusted
def liar(n: int) -> None:
    g.v = n
