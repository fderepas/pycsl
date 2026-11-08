r"""Test 1870 — gen #31 CONTROL for 1869 (expected PASS): the TRUE claim now proves.

The other half of the route, and the half that shows the repair is a CORRECTION and not a
ban: before it, `\length(\result) == 0` — which is simply true of `return []` — was
REFUSED (`Prover result is: Unknown`), while the false `== 1024` next door verified. A
model that refuses the truth and certifies the lie is the same defect seen from both sides.

The indirect spelling is covered too: `xs = []` followed by `return xs` behaved identically
on both halves, and the repair recognises a local bound ONCE to the placeholder with no
`_len` sidecar, no element store and no rebinding.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \length(\result) == 0
#@ assigns \nothing
def mk() -> list:
    return []


#@ ensures \length(\result) == 0
#@ assigns \nothing
def mk_local() -> list:
    xs = []
    return xs
