"""Test 1231 — the TRUE twin of 1230, and the second half of route #88's completeness gain.

Before the repair this was REFUSED while the FALSE claim (1230) proved. Now `init_body` is
keyed by FIELD and last-wins, and a later store the capture rule cannot express sets the slot
back to `None` rather than being ignored — so the later literal `3` is carried by
`field_defaults` (also last-wins now) and this TRUE claim PROVES.

The slot is set to `None` rather than popped ON PURPOSE: a field's position in `init_body`
stays at its FIRST capture, so a single-store constructor — every constructor in the corpus,
the mirror, `src/pycsl` and `src/pycsl_lib` — emits BYTE-IDENTICALLY.
"""


class C:
    n: int

    #@ assigns self.n
    def __init__(self, k: int) -> None:
        self.n = k
        self.n = 3


#@ requires True
#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    c = C(7)
    return c.n
