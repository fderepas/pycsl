r"""Test 1397 — ROUTES #136/#137 positive control, CORRECTED by route #229.

WHAT THIS FILE USED TO CLAIM, and it was false: "a BARE dynamic `exec` inside a function (its
assignments land in the discarded locals snapshot, so tests 0638/0639/0644 keep demonstrating
the `\in_scope` havoc and the frame taint) ... still prove." That parenthesis is the premise
route #229 refuted. A `global` DECLARATION inside the exec'd text redirects the assignment
away from the locals snapshot and into the GLOBALS mapping, which at function scope is still
the REAL module globals:

    N = 3
    def rebind(): code = "global N\nN = 5"; exec(code)
    def read() -> int: return N        under `#@ ensures \result == 3`

PROVED "All contracts formally proven"; CPython returns 5. A bare dynamic `exec` in a function
is therefore NOT confined, and it is now refused wherever it stands — the location gate
survives only for a CONSTANT `exec`, whose text is spliced in as real source and modelled.
The refuted arm moved to **1917**, an expected-FAIL witness.

THE FILE IS SPLIT RATHER THAN FLIPPED, deliberately. It was a positive control for THREE
things and route #229 refutes only one. The other two are still genuine positive controls and
must keep PASSING, because they are what would catch a repair that refused EVERYTHING instead
of refusing the one shape:

  * a CONSTANT `eval` with no walrus and none of `( . [` in its text (`eval("2 + 3")`) — a
    closed arithmetic expression that cannot bind or mutate anything;
  * a module-scope field store on a genuinely fresh module-class instance.

Flipping the whole file to expected-FAIL would have retired both controls in order to record
one refutation, and the refuse-everything failure mode would then have had nothing watching
it.
"""
# pycsl-expected: PASS# pycsl-expected: PASS
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0


g = C()
g.n = 5



#@ ensures \result == 0
#@ assigns \nothing
def h() -> int:
    if eval("2 + 3") == 5:
        return 0
    return 0
