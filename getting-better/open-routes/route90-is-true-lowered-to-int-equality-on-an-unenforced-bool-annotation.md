# ROUTE #90 — `is True` IS LOWERED TO INTEGER EQUALITY ON A `bool` ANNOTATION NOTHING ENFORCES

**STATUS: FOUND AND REPRODUCED 2026-09-12 (gen #12). BOTH DIRECTIONS MEASURED, PLUS A
CROSS-CALL ESCALATION AND A SECOND OPERATOR (`is not True`).**

**CLASS: the #69 class** — a FALSE POSTCONDITION about ordinary, TOTAL Python.

## THE EXPLOIT

```python
#@ requires x == 1
#@ ensures \result == 1
def f(x: bool) -> int:
    if x is True:
        return 1
    return 0
```

    CPython f(1):  0        # `1 is True` is False -- True is a distinct singleton object
    PyCSL:         [+] Verification SUCCESS! All contracts formally proven.

The TRUE twin (`\result == 0`) is REFUSED.

## THE EMISSION — READ IN FULL, AND THE DEFECT IS ON ONE LINE

```whyml
  let f (x: int) : int
    requires { (x = 1) }
    ensures  { (result = 1) } (* linear *)
  =
    try
    if (x = 1) then begin        (* <-- `x is True` BECAME `x = 1` *)
      raise (Return 1)
    end else begin
      raise (Return 0)
    end
    with Return r -> r end
```

`is True` is lowered to **integer equality against 1**, and the `bool` parameter is emitted as
a plain `int`. Under `requires x = 1` the guard is TRIVIALLY TRUE, so `result = 1` proves.
In CPython the guard is `1 is True`, which is **False**: `True` is a distinct singleton object
from the `int` 1, while `1 == True` is True. **THE MODEL DECIDES `is` AS `==`, AND FOR THE
BOOL SINGLETON THOSE ARE DIFFERENT RELATIONS ON EXACTLY THE INTEGERS 0 AND 1.**

## CARRIERS — BOTH DIRECTIONS, A CROSS-CALL ESCALATION, AND A SECOND OPERATOR

| carrier | shape | claim | CPython | PyCSL |
|---------|-------|-------|---------|-------|
| p11 | `x: bool`, `requires x == 1`, `x is True` | `\result == 1` | **0** | **PROVED** ❌ |
| p11t | same | `\result == 0` | 0 | refused |
| p12 | **CONTROL**, `requires x == 0` | `\result == 0` | 0 | PROVED ✔ (the arm fires and is decidable) |
| p13 | **CROSS-CALL**: `f()` returns `g(1)` | `\result == 1` | **0** | **PROVED** ❌ |
| p13t | same | `\result == 0` | 0 | refused |
| p14 | `x is not True` | `\result == 0` | **1** | **PROVED** ❌ |

**p13 IS THE ESCALATION AND IT IS THE PART THAT MAKES THIS SEVERITY-1.** The false
precondition is not merely *satisfiable in Python* — **PyCSL'S OWN FRONT-END ACCEPTS THE
INT LITERAL `1` AS THE ACTUAL FOR A `bool` PARAMETER**, so the whole lie is reachable from
PyCSL source, with no appeal to a hypothetical external caller.

## THE MECHANISM — TWO ROUTES THIS CAMPAIGN ALREADY CLOSED, NEVER COMPOSED

Route **#42** (`is` on a singleton) fenced `is` with a WHITELIST and **ADMITTED** the arm
`b: bool; if b is True:` — its own control — on the stated ground that *"the emitter can SHOW
`X` is a Python `bool`"*. It can show no such thing: it reads a **TYPE ANNOTATION**.

Route **#51** already proved, on a different shape, that **AN ANNOTATION IN THIS CODEBASE IS
NOT A FACT** — a `bool`-annotated binding can hold `1` or `2`.

**>>> #42's ADMITTED ARM IS SOUND ONLY UNDER #51's ALREADY-REFUTED ASSUMPTION. NEITHER ROUTE
IS WRONG IN ISOLATION; THE DEFECT LIVES IN THE COMPOSITION, AND NOBODY RAN IT. <<<**

This is the same one-level-up shape as #89 — where #83's fence was scoped by TYPE and #85/#87
widened what a TYPE can decide — but with a sharper moral: **#89 was a COMPLETENESS GAIN
re-arming a fence; #90 is a FENCE BUILT ON A FACT THE CAMPAIGN HAD ALREADY DISPROVED
ELSEWHERE.** A control that admits an arm "because we can show T" must cite the ENFORCEMENT
of T, not its DECLARATION.

## HOW IT WAS FOUND — AND THE VACUOUS FIRST ATTEMPT, RECORDED BECAUSE IT COST A ROUND

Generator 1 ("which single operation did that control actually run?"), applied to #42's
control table. The FIRST attempt put the claim on a *caller* of an uncontracted `g` — and
**ALL THREE DRIVERS REFUSED, INCLUDING THE POSITIVE CONTROL.** That is the signature of a
VACUOUS probe, not a fail-closed one: an uncontracted callee is opaque, so the `is True` arm
never fired at all. **A PROBE WHOSE OWN POSITIVE CONTROL REFUSES HAS MEASURED NOTHING** —
check the control before recording a no-finding. Moving the claim into the same function made
the arm fire (p12 proves), and the defect appeared immediately.

## THE PREDICTED REPAIR (not yet built — DO NOT SUPPLY A WITNESS)

The honest fix is to make `is True` / `is False` / `is not True` **fail-closed on any operand
whose bool-ness rests only on an annotation**, i.e. narrow #42's whitelist to operands the
emitter can show are bool BY CONSTRUCTION (a literal `True`/`False`, a comparison result, a
`bool()` call), not by declaration. **THE CAMPAIGN'S HARDEST-WON RULE APPLIES WITH FULL
FORCE: DO NOT "FIX" THIS BY SUPPLYING A WITNESS** — e.g. by emitting an invariant
`0 <= x <= 1` for every `bool`-annotated parameter. That would be a completeness fix
supplying a witness value, it would still be WRONG (it admits `x = 1`, the exact carrier),
and it would make a second falsehood decidable rather than fewer.

Cost must be MEASURED, not predicted. The gate that carries the claim is the one that
contains the blast radius: `is True`/`is False` against annotated bools in `src/pycsl_lib`
and the mirror are in NEITHER byte-diff corpus, so the **reference SUITE** prices those
(route #83's lesson), while the byte-diff prices the corpora.

## WITNESSES

`scratchpad/w62/r90/p11_is_true_annot_lie_inline.py`,
`p11t_is_true_annot_lie_inline_twin.py`, `p12_is_true_ctl_inline.py`,
`p13_is_true_crosscall_escalation.py`, `p13t_is_true_crosscall_twin.py`,
`p14_is_not_true_annot_lie.py`.
The vacuous first attempt is kept deliberately as a negative lesson:
`p9_is_true_bool_annotation_lie.py`, `p9t_…_twin.py`, `p10_is_true_ctl_real_bool.py`.
