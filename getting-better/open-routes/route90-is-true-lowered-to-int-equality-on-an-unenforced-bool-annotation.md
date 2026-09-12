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

## CARRIERS — AND THE TABLE IS THE FINDING, BECAUSE IT IS **INVERTED**

| carrier | operand's bool-ness comes from | claim | CPython | PyCSL |
|---------|-------------------------------|-------|---------|-------|
| p11 | **ANNOTATION** — param `x: bool`, `requires x == 1` | `\result == 1` | **0** | **PROVED** ❌ |
| p11t | same | `\result == 0` | 0 | refused |
| p12 | same, `requires x == 0` (**arm-fired control**) | `\result == 0` | 0 | PROVED ✔ |
| p13 | **ANNOTATION**, CROSS-CALL: `f()` returns `g(1)` | `\result == 1` | **0** | **PROVED** ❌ |
| p13t | same | `\result == 0` | 0 | refused |
| p14 | **ANNOTATION**, operator `is not True` | `\result == 0` | **1** | **PROVED** ❌ |
| p15 | **ANNOTATION**, operator `is False` | `\result == 1` | **0** | **PROVED** ❌ |
| p19 | **ANNOTATION** on a LOCAL — `y: bool = 1` | `\result == 1` | **0** | **PROVED** ❌ |
| p19t | same | `\result == 0` | 0 | refused |
| p16 | annotation on a **FIELD** (`Attribute`) | — | 0 | **REFUSED by the guard** |
| p17 | **CONSTRUCTION** — `y = a > b`, a comparison result | `\result == 1` | **1** | **REFUSED by the guard** |
| p18 | **CONSTRUCTION** — `y = True`, a bool LITERAL | `\result == 1` | **1** | **REFUSED by the guard** |

**>>> READ THE LAST THREE ROWS AGAINST THE FIRST SIX. THE WHITELIST IS NOT MERELY TOO
PERMISSIVE — IT IS ANTI-CORRELATED WITH ACTUAL BOOL-NESS. <<<** It **ADMITS** the one source
of bool-ness that nothing enforces (a type annotation, which route #51 already proved can
lie, and which p19 shows is enough even on a LOCAL initialised to `1`), and it **REFUSES**
the two sources that are bool BY CONSTRUCTION and therefore provably safe — a comparison
result and the bool literal `True` itself. Every admitted carrier is unsound; both refused
constructions are sound and true.

## THE GUARD'S OWN ERROR MESSAGE MEASURES THIS EXACT DEFECT — AND THEN RECOMMENDS IT

The refusal emitted for p17/p18 reads, verbatim:

> `an IDENTITY test against a bool literal (X is True / X is False) is refused unless the
> emitter can SHOW X is a Python bool (ROUTE #42). is is object identity against a SINGLETON,
> so X is True is False for every genuine int — Python's 1 is True is False — while PyCSL
> int-encodes bool, which would make the model decide the test as VALUE equality and prove
> the wrong branch: measured, x = 1; if x is True: return 7 proved \result == 7 where Python
> returns 0. Here X is a Var the emitter cannot type as bool.` **`Write X == True, or
> annotate X as bool.`**

Route #42 therefore **ALREADY MEASURED THIS EXPLOIT** — `x = 1; if x is True` proving the
wrong branch is *my* carrier, written down as the hazard the guard exists to prevent. And the
guard's closing remediation advice, **"annotate `X` as `bool`"**, is the attack: following the
message's own instruction converts a correct refusal into the proof of a falsehood.

**>>> A GUARD WHOSE ERROR MESSAGE CORRECTLY STATES THE UNSOUNDNESS IT PREVENTS CAN STILL BE
THE THING THAT CAUSES IT, IF ITS REMEDIATION ADVICE IS THE UNSOUND CASE. READ THE `HOW TO
FIX THIS` LINE OF EVERY FAIL-CLOSED MESSAGE AS AN ATTACK SURFACE. <<<** This campaign has
twice praised a refusal message for "stating the unsoundness that WOULD occur" (the
`reverse()`/`sort()` carve-out, gen #11's third probe round). That praise was for the
*diagnosis*. **Nobody had ever read the PRESCRIPTION.**

## THE MECHANISM — TWO ROUTES THIS CAMPAIGN ALREADY CLOSED, NEVER COMPOSED

Route **#42** (`is` on a singleton) fenced `is` with a whitelist and **ADMITTED** the arm
`b: bool; if b is True:` on the stated ground that *"the emitter can SHOW `X` is a Python
`bool`"*. It can show no such thing: it reads a **TYPE ANNOTATION**.

Route **#51** already proved, on a different shape, that **AN ANNOTATION IN THIS CODEBASE IS
NOT A FACT** — a `bool`-annotated binding can hold `1` or `2`.

**#42's ADMITTED ARM IS SOUND ONLY UNDER #51's ALREADY-REFUTED ASSUMPTION. NEITHER ROUTE IS
WRONG IN ISOLATION; THE DEFECT LIVES IN THE COMPOSITION, AND NOBODY RAN IT.** A control that
admits an arm "because we can show T" must cite the **ENFORCEMENT** of T, not its
**DECLARATION**.

## HOW IT WAS FOUND — AND THE VACUOUS FIRST ATTEMPT, RECORDED BECAUSE IT COST A ROUND

Generator 1 ("which single operation did that control actually run?"), applied to #42's
control table. The FIRST attempt put the claim on a *caller* of an uncontracted `g` — and
**ALL THREE DRIVERS REFUSED, INCLUDING THE POSITIVE CONTROL.** That is the signature of a
VACUOUS probe, not a fail-closed one: an uncontracted callee is opaque, so the `is True` arm
never fired at all. **A PROBE WHOSE OWN POSITIVE CONTROL REFUSES HAS MEASURED NOTHING** —
check the control before recording a no-finding. Moving the claim into the same function made
the arm fire (p12 proves), and the defect appeared immediately.

## THE PREDICTED REPAIR (not yet built — DO NOT SUPPLY A WITNESS)

The inverted table makes the repair unusually clean, because it is **A SOUNDNESS FIX AND A
COMPLETENESS GAIN IN THE SAME EDIT, IN OPPOSITE DIRECTIONS** — and it SUPPLIES NO WITNESS:

  * **REFUSE** the annotation-only operands that are admitted today (param, local, and any
    binding whose bool-ness comes from a declaration). That is the soundness half; it turns
    six proving falsehoods into refusals.
  * **ADMIT** the by-construction operands that are refused today — a `True`/`False` literal,
    a comparison result, a `bool()` call. That is the completeness half, it is provably
    sound, and p17/p18 are its positive witnesses (both TRUE and both refused today).
  * **FIX THE ERROR MESSAGE.** Its remediation line currently recommends the exploit and MUST
    stop saying "annotate `X` as `bool`"; the correct advice is `X == True`, which it already
    offers first. **THE CAMPAIGN'S HARDEST-WON RULE APPLIES WITH FULL
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
