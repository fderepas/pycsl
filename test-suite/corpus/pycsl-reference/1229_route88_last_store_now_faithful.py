"""Test 1229 — ROUTE #88's COMPLETENESS GAIN and its bounding positive witness.

The TRUE twin of 1228. Before the repair it was REFUSED while the FALSE claim proved; now the
field's default is taken from its LAST top-level store and this TRUE claim PROVES. The repair
is a FAITHFUL CAPTURE, not a refusal — the information was sitting in the constructor all
along, which is route #82's rule applied to store ORDER.

**WHY THE POSITIVE WITNESS IS LOAD-BEARING.** An over-broad repair — marking every
multiply-stored field unconstrained — would satisfy every expected-FAIL witness of this route
at once while destroying the capability. Only a file that must STILL PROVE can fail when the
guard grows too wide. 1211, 1215, 1219 and 1223 are the same instrument for routes #83, #79,
#85 and #87.
"""


class C:
    n: int

    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 1
        self.n = 2


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.n
