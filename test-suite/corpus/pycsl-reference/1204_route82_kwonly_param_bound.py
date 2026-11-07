"""Test 1204 — ROUTE #82: an `__init__` KEYWORD-ONLY parameter is now BOUND, not dropped.

`_collect_init_construction` built the constructor's formal set from `child.args.args` alone.
Python's AST keeps the other two parameter kinds in the SIBLING fields `posonlyargs` and
`kwonlyargs`, which were never read — so for a keyword-only `__init__` the parameter set came
back EMPTY, the `if not pset: break` fired, `init_params`/`init_body` were empty, and EVERY
field fell through to `_field_default`'s literal `0`. WL-07's keyword binding could not rescue
it either: that path binds keyword arguments BY NAME ONTO `init_params`, which is the very list
that came back empty.

Measured, before the repair:

    class P:
        v: int
        def __init__(self, *, v: int = 0) -> None:
            self.v = v
    P(v=7).v        #@ ensures \\result == 0     <-- PROVED; CPython returns 7

The TRUE twin was REFUSED, which is what made it a route rather than a gap, and THE CONTROL WAS
EXACT: the same class, the same field, the same argument value and the same clause with an
ORDINARY POSITIONAL parameter was FAITHFUL IN BOTH DIRECTIONS. Only the parameter KIND changed.

**THE REPAIR IS A FAITHFUL CAPTURE, NOT A REFUSAL — a completeness GAIN.** The parameter was
right there; there was no need to give up on it. So THIS FILE PROVES THE TRUE CLAIM, and 1207
carries the false one as the negative witness.

The two lists are kept SEPARATE on purpose: `init_params` is consumed by
`_call_record_constructor` as the POSITIONAL binding list (`args[i]` binds `init_params[i]`), so
appending the keyword-only names to it would bind them FROM POSITIONAL ARGUMENTS — something
Python never does, i.e. a DIFFERENT wrong model in place of the old one. Positional-only and
positional-or-keyword parameters DO bind positionally and belong in `init_params`;
keyword-only names travel separately as `init_kwonly_params` for the by-name binding.

Blast radius measured before building: 8 constructors repo-wide have keyword-only parameters and
NONE is in the verified corpus, 0 have positional-only parameters anywhere, and the emission is
byte-inert over both corpora (971/971, 2204/2204) with IR conformance 38/38 + 38/38.
"""


class P:
    v: int

    #@ assigns self.v
    def __init__(self, *, v: int = 0) -> None:
        self.v = v


#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    p = P(v=7)
    return p.v
