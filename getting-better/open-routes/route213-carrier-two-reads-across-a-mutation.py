r"""CARRIER for the OPEN route #213 (no-default form) — ROUTE #213: two reads of the SAME `getattr` are the same CONSTANT, across a
call that writes the attribute.

Route #197 made the unknown-class `getattr` device PER-SITE, and said why in its own
comment: "hashed on the call's IR so two reads of the SAME `getattr` expression agree
(which `(any int)` would NOT give — it is fresh at every evaluation, and losing that
equality is a real loss of faithfulness for no gain)". That equality is sound only while
the attribute CANNOT CHANGE between the reads.

MEASURED: this file PROVED `\result == 0`. The emission says why —

    val function pycsl_getattr_missing_1929893044 : int      (* a CONSTANT *)
    val setattr_3 (x: int) (f: int) (v: int) : unit writes { _pyobj_state }
    ...
    x := pycsl_getattr_missing_1929893044;
    (mutate o);
    y := pycsl_getattr_missing_1929893044;

— the device does not depend on the state it is supposed to read. CPython answers **-98**
for an object whose `a` is 1.

THE FAITHFUL FIX IS A STATE-KEYED DEVICE: `val function pycsl_getattr_missing_<h> (s: int)
: int` applied to `!_pyobj_state`, which KEEPS #197's equality for two reads with no
intervening write and loses it exactly across one. It changes emission at the two device
sites in `module6_whyml/expressions.py`, which is mirrored UN-trusted, so it costs a
verbatim mirror edit plus that file's whole-file re-proof (21347 goals) plus a corpus
byte-diff. That price is recorded; this window takes the refusal, which is keyed on exactly
the false-equality shape and has an EMPTY blast radius (zero functions in the corpus or in
`src/pycsl_lib/` read the same `getattr` expression twice in a function that also calls
something else).

Control: 1727 — two reads with NO intervening call still agree, which is route #197's
property and must not be lost.

IT LIVES OUTSIDE THE CORPUS ON PURPOSE. It PROVES today, so `# pycsl-expected: FAIL` would
be an XPASS (a red suite, by the rule that exists to catch a negative witness that starts
proving) and `PASS` would write "this false proof is expected" into the corpus.
`bin/check-open-route-carriers.py` runs it and asserts the recorded verdict; a CHANGE means
the route is probably closed and the entry must go in the same commit.

Run with: `--memory-model hoare`.
"""
from typing import Any

_ = 0  # anchor


#@ assigns o.a
def mutate(o: Any) -> None:
    o.a = 99


#@ assigns o.a
#@ ensures \result == 0
def f(o: Any) -> int:
    x = getattr(o, "a")
    mutate(o)
    y = getattr(o, "a")
    return x - y
