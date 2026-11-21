r"""Test 1917 — gen #33 (expected FAIL): ROUTE #229, the arm split out of 1397.

FALSE OF THE PROGRAM: after `rebind()`, CPython's `read()` returns 5, not 3. At the parent
commit this file PROVED `\result == 3` and reported "All contracts formally proven".

THE CARRIER IS A SCOPE ARGUMENT, in one of the best-audited comments in the tree.
`Module3_Weaver`'s dynamic-`exec` detector lists six measured falsehoods it closes, records
that its first cut keyed on `:=` was walked past by `eval("globals().update({'N': 5})")`, and
that the widened TOKEN rule was walked past by `eval("f.__globals__.__setitem__('N', 5)")`.
It abandoned both spelling rules for a structural one and carries a census over five trees.
What survived was the one premise nobody re-read:

    "assignments made by a bare `exec`/`eval` go to the LOCALS mapping, which IS the module
     globals at module and class-body scope and is a discarded snapshot inside a function.
     So a bare call in a function body is left alone"

True of the binding form it pictures — a plain assignment. A `global` DECLARATION inside the
exec'd text redirects the assignment into the GLOBALS mapping, and at function scope that is
still the real module globals. The snapshot is discarded; the assignment never went there.

>>> A SCOPE ARGUMENT ENUMERATES THE BINDING FORMS ITS AUTHOR PICTURED, AND `global` IS THE
>>> BINDING FORM WHOSE WHOLE PURPOSE IS TO DEFEAT THE SCOPE IT RESTS ON.

THE POPULATION WAS EXACTLY ONE SHAPE, and three neighbours were already refused — the same
exec at MODULE scope, a CONSTANT exec at function scope, and a dynamic
`eval("globals().update({'N': 5})")` at function scope. The asymmetry was precise: `eval` had
no function-scope exemption and `exec` did.

THE FIX IS NOT A SPELLING RULE. The text is DYNAMIC, so the emitter cannot read it at all and
any rule about its contents is unfounded by construction — which is exactly why the two
earlier spelling cuts failed. A non-constant `exec` now reaches wherever it stands, as a
non-constant `eval` already did; a CONSTANT `exec` keeps the location gate because its text
is spliced in as real source and is modelled.

Companion positive control: 1397, which keeps the two arms route #229 does NOT refute.
"""
# pycsl-expected: FAIL
N = 3


#@ ensures \result == 0
#@ assigns \nothing
def rebind() -> int:
    code = "global N\nN = 5"
    exec(code)
    return 0


#@ ensures \result == 3
#@ assigns \nothing
def read() -> int:
    return N
