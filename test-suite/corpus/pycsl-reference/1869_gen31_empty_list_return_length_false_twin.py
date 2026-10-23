r"""Test 1869 — gen #31 WITNESS (expected FAIL): a returned `[]` does not have length 1024.

THE ROUTE (#225). `[]` lowers to the placeholder `(Array.make 1024 0)`, and a Why3 array's length
is immutable, so the model of the empty list had length **1024**. This exact file — with
`Verification SUCCESS` — is what a certified FALSE postcondition looks like on ordinary
total Python: no `no_exception`, no opt-in, no `\trusted` anywhere, and `len(mk())` is 0 on
every run.

Route #159 had already found the mechanism and repaired it for a LOCAL, on the emitted
text, for ONE obligation (`in_bounds`) inside ONE syntactic scope. The RETURN carries the
false length ACROSS THE FUNCTION BOUNDARY, where a caller ASSUMES it — and an assumption of
`1024 = <the real length>` is contradictory, which makes every downstream goal vacuously
provable. That is the modular false-green already on file in
`getting-better/20260718-0633-stmt-list-append-mutation-wall-response.md`, where
`--check-vacuity` did not flag it either.

The control is 1870 (the TRUE claim, which used to be REFUSED and now proves) and 1871
(the append path, faithful all along and which this repair must not disturb).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \length(\result) == 1024
#@ assigns \nothing
def mk() -> list:
    return []
