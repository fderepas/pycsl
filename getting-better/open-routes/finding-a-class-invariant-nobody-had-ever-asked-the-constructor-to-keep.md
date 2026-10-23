# A class invariant nobody had ever asked the constructor to keep

Generation #31, 2026-09-26T02:15Z. Found because the `--slow` battery ran for the first time
this session, and its last remaining RED turned out not to be a resource problem.

## The verdict, and why it read as noise for so long

`bin/check-stdlib-modules-verify.py` said `re/__init__.py` was NEWLY NOT VERIFYING. The driver
said:

    File "…mlw", line 21, characters 178-193:
    Sub-goal goal of goal _check_class_inv_rematch.
    Prover result is: Unknown (why3: Out of
    memory) (22.15s, -1 steps).

**"Out of memory", 22 seconds, `-1` steps.** Every signal in that line says RESOURCE. The first
two hypotheses were exactly that: the box was loaded (the suite was running), and a sibling
goal really had reported `Timeout (25.26s, 11258882 steps)` against a 30-second limit. Both
were refuted by measurement — it fails identically on an IDLE box, and identically on the
pre-patch tree `85bfa846`, so neither load nor this session's emitter change explains it.

Reading the goal explains it in one line:

    goal _check_class_inv_rematch :
      forall _string _start _end _groups string start py_end groups : int.
        _string = string -> _start = start -> _end = py_end -> _groups = groups
        -> ((_start >= 0)) /\ ((_end >= _start))

**The goal is FALSE.** Nothing constrains `start`. `ReMatch(s, -1, -5, g)` refutes it. Alt-Ergo
does not answer `Invalid` here — it grinds on the integer quantification and dies out of
memory — so an unprovable goal wore the costume of an expensive one.

## Why the hole existed

`ReMatch` declares two class invariants:

    #@ class invariant self._start >= 0
    #@ class invariant self._end >= self._start
    class ReMatch:
        def __init__(self, string, start, end, groups):     # NO `#@ requires`
            self._string = string
            self._start = start
            self._end = end
            self._groups = groups

and the comment directly above those two lines is the whole history:

> (#34) THESE TWO `#@ class invariant` LINES USED TO SIT INSIDE THE CLASS BODY … both landed
> on `__init__`'s FunctionDef anchor … so both were SILENTLY DISCARDED and `ReMatch` carried
> NO invariants in the model at all.

So the sequence is: the invariants were written; they were discarded by a `#@`-binding bug; #34
fixed the binding, which turned them into REAL OBLIGATIONS; and the constructor that had never
been asked to establish them still could not. The module stopped verifying at that moment and
the plane that would have said so is in the `--slow` set.

**An instrument that starts working produces a red that looks like a regression.** It is not
one; it is the first honest measurement.

## The fix, and what it costs

    #@ requires start >= 0
    #@ requires end >= start
    def __init__(self, string, start, end, groups):

The goal gains its hypotheses — `… -> (start >= 0) -> (py_end >= start) -> …` — and
`re/__init__.py` reports `[+] Verification SUCCESS! All contracts formally proven.`

A `requires` on a constructor is a burden MOVED, not removed, so the honest accounting is who
now carries it. Measured: every `ReMatch(...)` construction in the tree is inside
`src/pycsl_lib/re/_engine.py` (ten of them), and `_engine.py` is REFUSED by the front end and
is in the plane's own baseline as such — so no VERIFIED caller acquires an obligation today,
and every one of the ten passes real match positions (`pos`, `i`, `pos + 1`) that satisfy it.
ZERO corpus programs import `re`, so the change is corpus-inert by construction.

The day `_engine.py` stops being refused, those ten constructions become ten obligations. That
is the correct outcome and it is the point of writing the precondition down.
